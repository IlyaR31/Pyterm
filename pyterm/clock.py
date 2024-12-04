import time


class Clock:
    def __init__(self):
        self.start_time = time.perf_counter()

    def tick(self, fps):
        elapsed_time = time.perf_counter() - self.start_time
        if elapsed_time < 1/fps:
            time.sleep(1/fps - elapsed_time)
        self.start_time = time.perf_counter()

    def get_fps(self):
        elapsed_time = time.perf_counter() - self.start_time
        self.start_time = time.perf_counter()
        return 1 / elapsed_time
