# async def function(), 定义了一个异步函数，异步函数可以暂停或者回复执行，而不必一次执行完毕
# await 就是说在执行某个语句的时候，可以先去执行其他协程，等这个语句有返回结果了再继续执行
# create task 里面应该是一个 async 函数，这个函数会被创建成一个 task，然后被加入到事件循环中


import asyncio
import contextlib
import json
from ControlSignal import ControlSignalClock, ControlSignalBase
from pupil_labs.realtime_api import (
    Device,
    Network,
    receive_gaze_data,
    receive_video_frames,
)
import typing as T
import cv2
import os

collect_data = False

async def main():
    # global collect_data
    control_signal = ControlSignalClock(interval=5)
    asyncio.create_task(control_signal.run())
    
    async with Network() as network:
        dev_info = await network.wait_for_new_device(timeout_seconds=5)
    if dev_info is None:
        print("No device could be found! Abort")
        return


    async with Device.from_discovered_device(dev_info) as device:
        status = await device.get_status()
        sensor_gaze = status.direct_gaze_sensor()
        if not sensor_gaze.connected:
            print(f"Gaze sensor is not connected to {device}")
            return
        
        sensor_world = status.direct_world_sensor()
        if not sensor_world.connected:
            print(f"Scene camera is not connected to {device}")
            return

        restart_on_disconnect = True
        
        queue_video = asyncio.Queue()
        queue_gaze = asyncio.Queue()
        
        process_video = asyncio.create_task(
            enqueue_sensor_data(
                receive_video_frames(sensor_world.url, run_loop=restart_on_disconnect),
                queue_video,
                control_signal
            )
        )
        process_gaze = asyncio.create_task(
            enqueue_sensor_data(
                receive_gaze_data(sensor_gaze.url, run_loop=restart_on_disconnect),
                queue_gaze,
                control_signal
            )
        )
        
        try:
            await save_query_data(queue_video, queue_gaze, control_signal)
        finally:
            process_video.cancel()
            process_gaze.cancel()
        
         
    
async def enqueue_sensor_data(sensor: T.AsyncIterator, queue: asyncio.Queue, control_signal: ControlSignalBase) -> None:
    ''' 将传感器的数据不断加入某个队列中 '''
    async for datum in sensor:
        if control_signal.is_active():
            try:
                queue.put_nowait((datum.datetime, datum))
            except asyncio.QueueFull:
                print(f"Queue is full, dropping {datum}")


async def save_query_data(queue_video: asyncio.Queue, queue_gaze: asyncio.Queue, control_signal: ControlSignalBase):
    ''' 保存数据 '''
    while True:
        if (not control_signal.is_active()) and control_signal.to_be_save():
            # get out all the data in both queue and save them
            print("saving data")
            video_data = []
            video_timestamp = []
            gaze_data = []
            while not queue_video.empty():
                timestamp, frame = await queue_video.get()
                video_data.append(frame.to_ndarray(format="bgr24"))
                video_timestamp.append(timestamp.timestamp())
            while not queue_gaze.empty():
                timestamp, gaze = await queue_gaze.get()
                gaze_data.append(gaze)
            data_dir = os.path.join("data", str(video_timestamp[0]))
            os.makedirs(data_dir, exist_ok=True)
            with open (os.path.join(data_dir, "gaze_data.json"), "w") as f:
                json.dump(gaze_data, f)
            with open (os.path.join(data_dir, "video_timestamp.json"), "w") as f:
                json.dump(video_timestamp, f)
            # use cv2 to save the video as mp4
            frame_height, frame_width, _ = video_data[0].shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(os.path.join(data_dir, "video.mp4"), fourcc, 30, (frame_width, frame_height))
            for frame in video_data:
                video.write(frame)
            video.release()
            print("data saved!")
            await control_signal.save_executed()
        await asyncio.sleep(1)
    



if __name__ == "__main__":
    print("entering")
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())