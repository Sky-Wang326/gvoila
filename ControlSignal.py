import asyncio
from abc import ABC, abstractmethod



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