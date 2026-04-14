from time import time

class Timer:
    def __init__(self):
        self.result = None

    def __enter__(self):
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time()
        self.result = end_time - self.start_time