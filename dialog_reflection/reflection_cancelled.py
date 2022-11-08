from dialog_reflection.cancelled_reason import (
    ICancelledReason,
)


class ReflectionCancelled(ValueError):
    def __init__(self, reason: ICancelledReason) -> None:
        self.reason = reason

    def __str__(self):
        return f"Reflection Cancelled. reason: {self.reason}"
