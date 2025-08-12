"""Incoming message metric"""

from typing import Optional

from prometheus_client import Counter, Gauge, Histogram

from ..monitoring import TimedMetric


class RabbitMQIncomingMessageMetric(TimedMetric):
    """Default context manager with request count, latency and in progress
    metrics.
    """

    MESSAGE_COUNT = Counter(
        'rabbitmq_messages_received',
        'Number of messages received',
        ['host', 'app_name', 'queue', 'exchange', 'routing_key', 'status']
    )

    MESSAGE_LATENCY = Histogram(
        'rabbitmq_received_message_latency',
        'Elapsed time per received mesage',
        ['host', 'app_name', 'queue', 'exchange', 'routing_key']
    )

    MESSAGE_IN_PROGRESS = Gauge(
        'rabbitmq_receive_message_in_progress',
        'Incoming messages in progress',
        ['host', 'app_name', 'queue', 'exchange', 'routing_key']
    )

    def __init__(
            self,
            host: str,
            app_name: str,
            queue: str,
            exchange: str,
            routing_key: Optional[str]
    ) -> None:
        super().__init__()
        self.host = host
        self.app_name = app_name
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key

    def on_enter(self) -> None:
        super().on_enter()
        self.MESSAGE_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.queue,
            self.exchange,
            self.routing_key
        ).inc()

    def on_exit(self) -> None:
        super().on_exit()
        self.MESSAGE_COUNT.labels(
            self.host,
            self.app_name,
            self.queue,
            self.exchange,
            self.routing_key,
            'ack' if self.error is None else 'nack'
        ).inc()
        self.MESSAGE_LATENCY.labels(
            self.host,
            self.app_name,
            self.queue,
            self.exchange,
            self.routing_key
        ).observe(self.elapsed)
        self.MESSAGE_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.queue,
            self.exchange,
            self.routing_key
        ).dec()
