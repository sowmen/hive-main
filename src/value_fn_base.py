from abc import ABC, abstractmethod

class ValueFunction(ABC):
    """
    Abstract base for user-supplied value functions.
    Ensure that only a float is returned.
    """

    @abstractmethod
    def __call__(self, report: dict) -> float:
        """
        Compute a single numeric score from a PPA report.
        Must be implemented by the user.

        Args:
            report (dict): PPA report data as a dictionary.

        Returns:
            float: Score representing the quality/value of the report.
        """
        pass

    def validate_return(self, value):
        """
        Validate that a value is a float and safe to use.
        """
        if not isinstance(value, (float, int)):
            raise TypeError(
                f"ValueFunction must return a float or int, got {type(value).__name__}"
            )
        value = float(value)
        if value != value:  # NaN check
            raise ValueError("ValueFunction returned NaN")
        if value == float("inf") or value == float("-inf"):
            raise ValueError("ValueFunction returned infinity")
        return value