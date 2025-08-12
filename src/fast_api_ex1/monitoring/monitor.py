"""Monitors"""

from contextlib import contextmanager
from typing import TypeVar, Iterator


from .metrics import Metric

TMetric = TypeVar('TMetric', bound=Metric)


@contextmanager
def monitor(metric: TMetric) -> Iterator[TMetric]:
    """Monitor an operation

    Args:
        metric (TMetric): The metric to update in the monitored session.

    Raises:
        metric.error: If the enclosed block raises an exception.

    Yields:
        Iterator[TMetric]: The context managed metric
    """
    try:
        metric.on_enter()
        yield metric
    except Exception as error:  # pylint: disable=broad-except
        metric.error = error
    finally:
        metric.on_exit()
        if metric.error:
            raise metric.error
