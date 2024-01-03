import asyncio
from abc import ABC, abstractmethod
import socket


class ControlSignalBase:
    def __init__(self):
        self._active = False
        self._2bsave = False
        
    def start(self) -> bool:
        if self._2bsave:
            return False
        print(" start flag set ")
        self._active = True
        self._2bsave = True
        return True
    
    def stop(self):
        print(" start flag reset ")
        self._active = False
        
    async def save_executed(self):
        print(" save flag reset ")
        self._2bsave = False
    
    def is_active(self):
        return self._active
    
    def to_be_save(self):
        return self._2bsave
    
    @abstractmethod
    async def run(self):
        pass
    

class ControlSignalClock(ControlSignalBase):
    def __init__(self, interval):
        super().__init__()
        self._interval = interval
    
    async def run(self):
        while True:
            await asyncio.sleep(self._interval)
            while not self.start():
                await asyncio.sleep(1)
            await asyncio.sleep(self._interval)
            self.stop()
            break
        
class ControlSignalWiFiButton(ControlSignalBase):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        # self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.tcp_socket.connect((self.ip, self.port))
    
    async def connect_to_server(self):
        self.tcp_reader, self.tcp_writer = await asyncio.open_connection(self.ip, self.port)
        print(f"WiFi button connected! Address {self.ip}:{self.port}")
        
        
    async def run(self):
        self.tcp_reader, self.tcp_writer = await asyncio.open_connection(self.ip, self.port)
        print(f"WiFi button connected! Address {self.ip}:{self.port}")
        while True:
            print("waiting for data")
            # data = self.tcp_socket.recv(1024)
            data = await self.tcp_reader.read(1024)
            print(data)
            if data:
                print(f"received data: {data}")
                if data == b'button pressed!':
                    if not self.is_active():
                        while not self.start():
                            await asyncio.sleep(1)
                        print("start signal")
                    else:
                        self.stop()
                        print("stop signal")
            else:
                raise Exception("WiFi button connection broken")
            await asyncio.sleep(1)
                    
                    
if __name__ == '__main__':
    async def test():
        
        # await control_signal.connect_to_server()
        asyncio.create_task(control_signal.run())
        # control_signal.run()
    
    control_signal = ControlSignalWiFiButton('192.168.31.125', 3328)
    asyncio.run(control_signal.run())