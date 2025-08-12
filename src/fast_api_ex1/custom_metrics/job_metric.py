"""Job metric"""

from prometheus_client import Counter, Gauge, Histogram

from ..monitoring import TimedMetric


class JobMetric(TimedMetric):
    """Default context manager with request count, latency and in progress
    metrics.
    """

    JOB_COUNT = Counter(
        'job_called',
        'Number of times job was called',
        ['host', 'app_name', 'job_name', 'status']
    )

    JOB_LATENCY = Histogram(
        'job_latency',
        'Elapsed time per job',
        ['host', 'app_name', 'job_name']
    )

    JOB_IN_PROGRESS = Gauge(
        'job_in_progress',
        'job in progress',
        ['host', 'app_name', 'job_name']
    )

    def __init__(
            self,
            host: str,
            app_name: str,
            job_name: str,
    ) -> None:
        super().__init__()
        self.host = host
        self.app_name = app_name
        self.job_name = job_name

    def on_enter(self) -> None:
        super().on_enter()
        self.JOB_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.job_name,
        ).inc()

    def on_exit(self) -> None:
        super().on_exit()
        self.JOB_COUNT.labels(
            self.host,
            self.app_name,
            self.job_name,
            'ok' if self.error is None else 'error'
        ).inc()
        self.JOB_LATENCY.labels(
            self.host,
            self.app_name,
            self.job_name,
        ).observe(self.elapsed)
        self.JOB_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.job_name,
        ).dec()
