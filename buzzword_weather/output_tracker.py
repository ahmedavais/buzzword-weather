from typing import Generic, TypeVar

Output = TypeVar("Output")


class OutputTracker(Generic[Output]):
    def __init__(self):
        self.data: list[Output] = []


class OutputListener(Generic[Output]):
    def __init__(self):
        self._trackers: list[OutputTracker[Output]] = []

    def track(self) -> OutputTracker[Output]:
        tracker: OutputTracker[Output] = OutputTracker()
        self._trackers.append(tracker)
        return tracker

    def emit(self, output: Output) -> None:
        for tracker in self._trackers:
            tracker.data.append(output)
