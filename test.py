from threading import Thread
import time

MAX = 1000
delay = .02

class TestThread(Thread):
    def __init__(self, n):
        super().__init__()
        self.n = n
    
    def run(self):
        time.sleep(self.n*delay)
        while(True):
            print(self.n)
            time.sleep(MAX*delay)

threads = []

for i in range(MAX):
    thread = TestThread(i)
    thread.start()
    threads.append(thread)

#for t in threads:
#    t.join()
