"""Outgoing message metric"""

from typing import Optional

from ..monitoring import TimedMetric
from prometheus_client import Counter, Gauge, Histogram


class RabbitMQOutgoingMessageMetric(TimedMetric):
    """Default context manager with request count, latency and in progress
    metrics.
    """

    MESSAGE_COUNT = Counter(
        'rabbitmq_messages_sent',
        'Number of messages sent',
        ['host', 'app_name', 'exchange', 'routing_key', 'status']
    )

    MESSAGE_LATENCY = Histogram(
        'rabbitmq_sent_message_latency',
        'Elapsed time per sent mesage',
        ['host', 'app_name', 'exchange', 'routing_key']
    )

    MESSAGE_IN_PROGRESS = Gauge(
        'rabbitmq_send_message_in_progress',
        'Outgoing messages in progress',
        ['host', 'app_name', 'exchange', 'routing_key']
    )

    def __init__(
            self,
            host: str,
            app_name: str,
            exchange: str,
            routing_key: Optional[str]
    ) -> None:
        super().__init__()
        self.host = host
        self.app_name = app_name
        self.exchange = exchange
        self.routing_key = routing_key

    def on_enter(self) -> None:
        super().on_enter()
        self.MESSAGE_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.exchange,
            self.routing_key
        ).inc()

    def on_exit(self) -> None:
        super().on_exit()
        self.MESSAGE_COUNT.labels(
            self.host,
            self.app_name,
            self.exchange,
            self.routing_key,
            'success' if self.error is None else 'failure'
        ).inc()
        self.MESSAGE_LATENCY.labels(
            self.host,
            self.app_name,
            self.exchange,
            self.routing_key
        ).observe(self.elapsed)
        self.MESSAGE_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.exchange,
            self.routing_key
        ).dec()
