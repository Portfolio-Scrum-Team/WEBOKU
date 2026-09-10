"""Timer mechanics for Weboku."""

from __future__ import annotations

import time

# Time allowed for each objective attempt.
#
# Beginner     = 10 minutes
# Intermediate = 6 minutes
# Advanced     = 2 minutes (preserved for existing compatibility)
# Pro          = 2 minutes
DIFFICULTY_SECONDS = {
    "beginner": 10 * 60,
    "intermediate": 6 * 60,
    "advanced": 2 * 60,
    "pro": 2 * 60,
}


class GameTimer:
    """Countdown timer used by the Weboku game."""

    def __init__(self, seconds):
        if seconds <= 0:
            raise ValueError("Timer duration must be greater than 0")

        self.seconds = seconds
        self._start_time = None
        self._elapsed_before_stop = 0

    def start(self):
        """Start the timer if it is not already running."""
        if self._start_time is None:
            self._start_time = time.monotonic()

    def stop(self):
        """Stop the timer and preserve the elapsed time."""
        if self._start_time is not None:
            self._elapsed_before_stop += time.monotonic() - self._start_time
            self._start_time = None

    def reset(self):
        """Reset the timer to its initial state."""
        self._start_time = None
        self._elapsed_before_stop = 0

    @property
    def elapsed(self):
        """Return the number of seconds elapsed."""
        if self._start_time is None:
            return self._elapsed_before_stop

        return self._elapsed_before_stop + (time.monotonic() - self._start_time)

    @property
    def remaining(self):
        """Return the number of seconds remaining, never below zero."""
        return max(0, self.seconds - self.elapsed)

    @property
    def expired(self):
        """Return True when the countdown has reached zero."""
        return self.remaining <= 0

    @property
    def remaining_seconds(self):
        """Return remaining whole seconds for CLI display."""
        return max(0, int(self.remaining))

    @property
    def display(self):
        """Return the countdown as MM:SS."""
        remaining = self.remaining_seconds
        minutes, seconds = divmod(remaining, 60)
        return f"{minutes:02d}:{seconds:02d}"
