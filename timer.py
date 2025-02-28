import time

class Timer:
    def __init__(self):
        self.start_time = time.time()

    def stop(self):
        return time.time() - self.start_time

    def reset(self):
        self.start_time = time.time()

    def get_elapsed_time(self):
        return time.time() - self.start_time

    def pause(self):
        self.paused_time = time.time()
        self.is_paused_flag = True

    def resume(self):
        self.start_time += time.time() - self.paused_time
        self.is_paused_flag = False

    def is_paused(self):
        return getattr(self, 'is_paused_flag', False)

    def is_running(self):
        return not self.is_paused() and self.get_elapsed_time() > 0

    def get_remaining_time(self, duration):
        if self.is_paused():
            return max(0, duration - (self.paused_time - self.start_time))
        return max(0, duration - self.get_elapsed_time())
