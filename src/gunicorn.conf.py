# gunicorn.conf.py
# Production Gunicorn configuration for Flask application

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 3000)}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'k8s-env-display'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = 1001
group = 1001
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

# Environment
raw_env = [
    f'FLASK_ENV=production',
    f'PYTHONPATH=/app'
]

# Preload app for better performance
preload_app = True

# Graceful timeout for worker restart
graceful_timeout = 30

# Worker tmp directory
worker_tmp_dir = "/dev/shm"

# Maximum number of pending connections
listen = 1024