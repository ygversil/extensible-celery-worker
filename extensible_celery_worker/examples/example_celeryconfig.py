"""Example Celery application and worker configuration."""

# URL to listen for tasks
broker_url = 'amqp://excewo:password@rabbitmq.priv.example.org/excewo'

# Do not store results
result_backend = None

# Make tasks ignore results to speed things
task_ignore_result = True

# Save tasks timestamp in UTC
enable_utc = True

# Local timezone
timezone = 'Europe/Paris'

# Notify of events during task execution so that they can be monitored
worker_send_task_events = True
