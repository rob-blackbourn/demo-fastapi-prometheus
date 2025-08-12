"""Work metric"""

from prometheus_client import Counter, Gauge, Histogram

from ..monitoring import TimedMetric


class WorkMetric(TimedMetric):
    """Default context manager with request count, latency and in progress
    metrics.
    """

    WORK_COUNT = Counter(
        'work_called',
        'Number of times work was called',
        ['host', 'app_name', 'work_name', 'status']
    )

    WORK_LATENCY = Histogram(
        'work_latency',
        'Elapsed time per work',
        ['host', 'app_name', 'work_name']
    )

    WORK_IN_PROGRESS = Gauge(
        'work_in_progress',
        'Work in progress',
        ['host', 'app_name', 'work_name']
    )

    def __init__(
            self,
            host: str,
            app_name: str,
            work_name: str,
    ) -> None:
        super().__init__()
        self.host = host
        self.app_name = app_name
        self.work_name = work_name

    def on_enter(self) -> None:
        super().on_enter()
        self.WORK_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.work_name,
        ).inc()

    def on_exit(self) -> None:
        super().on_exit()
        self.WORK_COUNT.labels(
            self.host,
            self.app_name,
            self.work_name,
            'ok' if self.error is None else 'error'
        ).inc()
        self.WORK_LATENCY.labels(
            self.host,
            self.app_name,
            self.work_name,
        ).observe(self.elapsed)
        self.WORK_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.work_name,
        ).dec()
