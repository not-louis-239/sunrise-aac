import time
from dataclasses import dataclass, field


@dataclass
class Interval:
    t_i: float
    t_f: float

    @property
    def duration(self) -> float:
        return self.t_f - self.t_i


@dataclass
class IntervalDiagnostic:
    intervals: list[Interval] = field(default_factory=list)

    def add(self, obj: Interval) -> None:
        self.intervals.append(obj)

    def prune(self, max_len: int) -> None:
        """Prune to keep only the most recent `max_len` intervals"""
        if max_len <= 0:
            raise ValueError("max_len must be a positive integer")

        self.intervals = self.intervals[-max_len:]

    def prune_seconds(self, t: float) -> None:
        """Prune intervals to only those whose initial time is within the last `t` seconds"""

        self.intervals = self.get_intervals_from_last(t)

    def get_intervals_from_last(self, t: float) -> list[Interval]:
        """Get all the time intervals whose initial time is within the last `t` seconds"""

        now = time.perf_counter()
        cutoff = now - t
        return [interval for interval in self.intervals if interval.t_i >= cutoff]

    def avg_freq_from_last(self, t: float) -> float:
        """Get the average frequency at which time intervals have been
        recorded in the last `t` seconds.
        Note that this is not the same as the average duration of each interval."""

        recent = self.get_intervals_from_last(t)

        if not recent:
            return 0  # no entries, so no valid frequency

        now = time.perf_counter()
        time_since_first = now - recent[0].t_i

        if time_since_first == 0:
            return 0  # guard against ZeroDivisionError

        return len(recent) / time_since_first

    def get_durations(self) -> list[float]:
        return [t.duration for t in self.intervals]
