import time


DIFFICULTY_SECONDS = {
    "beginner": 600,
    "intermediate": 300,
    "advanced": 120,
    "pro": 60,
}


class GameTimer:
    def __init__(self, seconds):
        if seconds <= 0:
            raise ValueError("Timer duration must be greater than 0")

        self.seconds = seconds
        self._start_time = None
        self._elapsed_before_stop = 0

    def start(self):
        if self._start_time is None:
            self._start_time = time.monotonic()

    def stop(self):
        if self._start_time is not None:
            self._elapsed_before_stop += time.monotonic() - self._start_time
            self._start_time = None

    def reset(self):
        self._start_time = None
        self._elapsed_before_stop = 0

    @property
    def elapsed(self):
        if self._start_time is None:
            return self._elapsed_before_stop

        return self._elapsed_before_stop + (
            time.monotonic() - self._start_time
        )

    @property
    def remaining(self):
        return max(0, self.seconds - self.elapsed)

    @property
    def expired(self):
        return self.elapsed >= self.seconds