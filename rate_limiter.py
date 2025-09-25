import time
import threading
from collections import deque
from contextlib import contextmanager


class RateLimiter:

    def __init__(self, max_requests: int, period: int):

        self.max_requests = max_requests
        self.period = period
        self.requests = deque()
        self.lock = threading.Lock()
        

    def acquire(self):
        
        while True:
            with self.lock:

                now = time.monotonic()

                while self.requests and now - self.requests[0] >= self.period:
                    self.requests.popleft()

                if len(self.requests) < self.max_requests:
                    self.requests.append(now)
                    return
                
                wait_time = self.period - (now - self.requests[0])
            
            time.sleep(wait_time)

    @contextmanager
    def limit(self):
        self.acquire()
        try:
            yield
        finally:
            pass

