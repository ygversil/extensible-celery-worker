"""Example Celery application and worker configuration."""

# URL to listen for tasks
broker_url = 'amqp://'

# URL to save task results
result_backend = 'redis://'

# Tasks must take care of saving results
task_ignore_result = False

# Save tasks timestamp in UTC
enable_utc = True

# Local timezone
timezone = 'UTC'

# Do not monitor tasks
worker_send_tasks_events = False
