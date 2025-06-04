#!/usr/bin/env python3
"""
Production-Ready Flask Application
Updated version that works properly in production environments
"""

import json
import logging
import os
import platform
import signal
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil
from flask import Flask, jsonify, render_template_string, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest

# Configure production-ready logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/tmp/app.log") if os.path.exists("/tmp") else logging.NullHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Initialize Flask app with production settings
app = Flask(__name__)
app.config.update(
    JSON_SORT_KEYS=False,
    # Production security settings
    SECRET_KEY=os.environ.get("SECRET_KEY", os.urandom(32)),
    # Disable debug mode in production
    DEBUG=False,
    # Production JSON settings
    JSONIFY_PRETTYPRINT_REGULAR=False,
)

# Application start time for uptime calculation
START_TIME = time.time()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "flask_app_requests_total", "Total number of requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram(
    "flask_app_request_duration_seconds", "Request latency", ["method", "endpoint"]
)
MEMORY_USAGE_GAUGE = Gauge("flask_app_memory_usage_bytes", "Current memory usage in bytes")
CPU_USAGE_GAUGE = Gauge("flask_app_cpu_usage_percent", "Current CPU usage percentage")
UPTIME_GAUGE = Gauge("flask_app_uptime_seconds", "Application uptime in seconds")
ACTIVE_REQUESTS = Gauge("flask_app_active_requests", "Number of active requests")


def is_production():
    """Detect if running in production environment"""
    return (
        os.environ.get("FLASK_ENV") == "production"
        or os.environ.get("ENVIRONMENT") == "production"
        or "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
        or "uwsgi" in os.environ.get("SERVER_SOFTWARE", "")
    )


def safe_read_file(file_path):
    """Safely read file contents"""
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return "File not found"
    except Exception as e:
        logger.warning(f"Error reading file {file_path}: {e}")
        return f"Error reading file: {str(e)}"


def safe_read_dir(dir_path):
    """Safely read directory contents"""
    try:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            return [item.name for item in path.iterdir()]
        return []
    except Exception as e:
        logger.warning(f"Error reading directory {dir_path}: {e}")
        return [f"Error reading directory: {str(e)}"]


def get_memory_info():
    """Get memory information in MB"""
    try:
        memory = psutil.virtual_memory()
        return {
            "total": round(memory.total / 1024 / 1024),
            "available": round(memory.available / 1024 / 1024),
            "used": round(memory.used / 1024 / 1024),
            "percent": memory.percent,
        }
    except Exception as e:
        logger.error(f"Error getting memory info: {e}")
        return {"total": 0, "available": 0, "used": 0, "percent": 0}


def get_cpu_info():
    """Get CPU information"""
    try:
        return {
            "count": psutil.cpu_count(),
            "percent": psutil.cpu_percent(interval=1),
            "load_avg": os.getloadavg() if hasattr(os, "getloadavg") else [0, 0, 0],
        }
    except Exception as e:
        logger.error(f"Error getting CPU info: {e}")
        return {"count": 1, "percent": 0, "load_avg": [0, 0, 0]}


def get_process_info():
    """Get current process information"""
    try:
        process = psutil.Process()
        return {
            "pid": process.pid,
            "ppid": process.ppid(),
            "memory_percent": round(process.memory_percent(), 2),
            "cpu_percent": round(process.cpu_percent(), 2),
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
            "uptime": round(time.time() - START_TIME, 2),
            "num_threads": process.num_threads(),
        }
    except Exception as e:
        logger.error(f"Error getting process info: {e}")
        return {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "memory_percent": 0,
            "cpu_percent": 0,
            "create_time": datetime.now().isoformat(),
            "uptime": round(time.time() - START_TIME, 2),
            "num_threads": 1,
        }


def get_server_info():
    """Get production server information"""
    return {
        "server_software": os.environ.get("SERVER_SOFTWARE", "Unknown"),
        "wsgi_server": "gunicorn" if "gunicorn" in os.environ.get("SERVER_SOFTWARE", "") else "development",
        "is_production": is_production(),
        "flask_env": os.environ.get("FLASK_ENV", "development"),
        "debug_mode": app.debug,
        "worker_pid": os.getpid(),
        "worker_ppid": os.getppid(),
    }


def adjust_color(color, amount):
    """Adjust color brightness"""
    try:
        color = color.lstrip("#")
        rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        adjusted = []
        for c in rgb:
            new_c = c + amount
            adjusted.append(max(0, min(255, new_c)))
        return f"#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}"
    except Exception:
        return color


def get_environment_info():
    """Collect comprehensive environment information"""
    memory_info = get_memory_info()
    cpu_info = get_cpu_info()
    process_info = get_process_info()
    server_info = get_server_info()

    # Collect environment variables (hide sensitive ones)
    env_vars = {}
    for key, value in os.environ.items():
        if any(sensitive in key.upper() for sensitive in ["SECRET", "PASSWORD", "TOKEN", "KEY"]):
            env_vars[key] = "[HIDDEN]"
        else:
            env_vars[key] = value

    return {
        "kubernetes": {
            "pod_name": os.environ.get("POD_NAME", "unknown"),
            "pod_namespace": os.environ.get("POD_NAMESPACE", "unknown"),
            "host_ip": os.environ.get("FROM_FIELD", "unknown"),
        },
        "application": {
            "environment": os.environ.get("ENVIRONMENT", "unknown"),
            "uptime": process_info["uptime"],
            "timestamp": datetime.now().isoformat(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "pid": process_info["pid"],
            "ppid": process_info["ppid"],
        },
        "server": server_info,
        "system": {
            "hostname": socket.gethostname(),
            "cpu_count": cpu_info["count"],
            "cpu_percent": cpu_info["percent"],
            "load_avg": cpu_info["load_avg"],
            "memory_total_mb": memory_info["total"],
            "memory_available_mb": memory_info["available"],
            "memory_used_mb": memory_info["used"],
            "memory_percent": memory_info["percent"],
        },
        "process": process_info,
        "volumes": {"shared_files": safe_read_dir("/app/share"), "secret_store": safe_read_dir("/mnt/secret-store")},
        "environment_variables": dict(sorted(env_vars.items())),
    }


@app.route("/healthcheck.html")
def health_check():
    """Health check endpoint for Kubernetes probes"""
    probe = request.args.get("probe", "unknown")
    timestamp = datetime.now().isoformat()
    process_info = get_process_info()
    server_info = get_server_info()

    health_status = {
        "status": "healthy",
        "probe": probe,
        "timestamp": timestamp,
        "uptime": process_info["uptime"],
        "memory_usage": f"{get_memory_info()['percent']:.1f}%",
        "pid": process_info["pid"],
        "server": server_info["wsgi_server"],
    }

    # Return HTML format as expected by Kubernetes manifest
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Health Check - {probe}</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Health Check: {probe}</h1>
        <pre>{json.dumps(health_status, indent=2)}</pre>
    </body>
    </html>
    """

    return html_content, 200, {"Content-Type": "text/html"}


@app.route("/")
def index():
    """Main application endpoint - displays environment information"""
    bg_color = os.environ.get("BG_COLOR", "#1e3a8a")
    font_color = os.environ.get("FONT_COLOR", "#ffffff")
    environment = os.environ.get("ENVIRONMENT", "unknown")

    env_info = get_environment_info()

    # Enhanced HTML template with server information
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Environment Display - {{ environment }}</title>
        <style>
            body {
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                background: linear-gradient(135deg, {{ bg_color }}, {{ bg_color_dark }});
                color: {{ font_color }};
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            .environment-badge {
                display: inline-block;
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
            }
            .server-badge {
                display: inline-block;
                padding: 4px 12px;
                background: {{ 'rgba(0, 255, 0, 0.3)' if server_mode == 'gunicorn' else 'rgba(255, 165, 0, 0.3)' }};
                border-radius: 15px;
                font-size: 0.8em;
                margin-left: 10px;
            }
            .section {
                background: rgba(255, 255, 255, 0.05);
                margin: 20px 0;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid {{ font_color }};
            }
            .section h3 {
                margin-top: 0;
                color: {{ font_color }};
                border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                padding-bottom: 10px;
            }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .info-item {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 8px;
            }
            .label {
                font-weight: bold;
                color: {{ font_color_light }};
            }
            .value {
                margin-left: 10px;
                word-break: break-all;
            }
            .list {
                list-style: none;
                padding: 0;
            }
            .list li {
                padding: 5px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            .refresh-btn {
                position: fixed;
                top: 20px;
                right: 20px;
                background: {{ font_color }};
                color: {{ bg_color }};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                text-decoration: none;
            }
            .timestamp {
                font-size: 0.9em;
                opacity: 0.7;
            }
            .metric-box {
                background: rgba(0, 0, 0, 0.3);
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
            }
            .production-indicator {
                color: {{ '#00ff00' if is_production else '#ffaa00' }};
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <a href="/" class="refresh-btn">🔄 Refresh</a>
        
        <div class="container">
            <div class="header">
                <h1>🐍 Kubernetes Environment Display (Flask)</h1>
                <div class="environment-badge">{{ environment_upper }}</div>
                <span class="server-badge">{{ server_mode }}</span>
                <div class="production-indicator">{{ production_status }}</div>
                <div class="timestamp">Last updated: {{ timestamp }}</div>
            </div>

            <div class="info-grid">
                <div class="section">
                    <h3>🎯 Kubernetes Information</h3>
                    <div class="info-item">
                        <div><span class="label">Pod Name:</span><span class="value">{{ pod_name }}</span></div>
                        <div><span class="label">Namespace:</span><span class="value">{{ pod_namespace }}</span></div>
                        <div><span class="label">Host IP:</span><span class="value">{{ host_ip }}</span></div>
                    </div>
                </div>

                <div class="section">
                    <h3>🖥️ Server Information</h3>
                    <div class="info-item">
                        <div><span class="label">WSGI Server:</span><span class="value">{{ server_mode }}</span></div>
                        <div><span class="label">Production Mode:</span><span class="value">{{ is_production }}</span></div>
                        <div><span class="label">Debug Mode:</span><span class="value">{{ debug_mode }}</span></div>
                        <div><span class="label">Worker PID:</span><span class="value">{{ worker_pid }}</span></div>
                        <div><span class="label">Server Software:</span><span class="value">{{ server_software }}</span></div>
                    </div>
                </div>

                <div class="section">
                    <h3>📊 Application Status</h3>
                    <div class="info-item">
                        <div><span class="label">Environment:</span><span class="value">{{ environment }}</span></div>
                        <div><span class="label">Uptime:</span><span class="value">{{ uptime }} seconds</span></div>
                        <div><span class="label">Python Version:</span><span class="value">{{ python_version }}</span></div>
                        <div><span class="label">Platform:</span><span class="value">{{ platform }}</span></div>
                        <div><span class="label">Architecture:</span><span class="value">{{ architecture }}</span></div>
                        <div><span class="label">Process ID:</span><span class="value">{{ pid }}</span></div>
                    </div>
                </div>

                <div class="section">
                    <h3>💻 System Information</h3>
                    <div class="info-item">
                        <div><span class="label">Hostname:</span><span class="value">{{ hostname }}</span></div>
                        <div><span class="label">CPU Cores:</span><span class="value">{{ cpu_count }}</span></div>
                        <div><span class="label">CPU Usage:</span><span class="value">{{ cpu_percent }}%</span></div>
                        <div class="metric-box">
                            <div><span class="label">Memory:</span></div>
                            <div>Total: {{ memory_total }} MB</div>
                            <div>Used: {{ memory_used }} MB ({{ memory_percent }}%)</div>
                            <div>Available: {{ memory_available }} MB</div>
                        </div>
                        <div><span class="label">Load Average:</span><span class="value">{{ load_avg }}</span></div>
                    </div>
                </div>

                <div class="section">
                    <h3>⚡ Process Information</h3>
                    <div class="info-item">
                        <div><span class="label">PID:</span><span class="value">{{ pid }}</span></div>
                        <div><span class="label">Parent PID:</span><span class="value">{{ ppid }}</span></div>
                        <div><span class="label">Threads:</span><span class="value">{{ num_threads }}</span></div>
                        <div><span class="label">Memory Usage:</span><span class="value">{{ process_memory }}%</span></div>
                        <div><span class="label">CPU Usage:</span><span class="value">{{ process_cpu }}%</span></div>
                        <div><span class="label">Start Time:</span><span class="value">{{ create_time }}</span></div>
                    </div>
                </div>

                <div class="section">
                    <h3>📁 Mounted Volumes</h3>
                    <div class="info-item">
                        <div><span class="label">Shared Files (/app/share):</span></div>
                        <ul class="list">
                            {{ shared_files_list }}
                        </ul>
                        <div><span class="label">Secret Store (/mnt/secret-store):</span></div>
                        <ul class="list">
                            {{ secret_files_list }}
                        </ul>
                    </div>
                </div>
            </div>

            <div class="section">
                <h3>🔧 Environment Variables</h3>
                <div class="info-item">
                    <ul class="list">
                        {{ env_vars_list }}
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Prepare template variables
    server_info = env_info["server"]
    template_vars = {
        "bg_color": bg_color,
        "bg_color_dark": adjust_color(bg_color, -20),
        "font_color": font_color,
        "font_color_light": adjust_color(font_color, 20),
        "environment": environment,
        "environment_upper": environment.upper(),
        "timestamp": env_info["application"]["timestamp"],
        # Server information
        "server_mode": server_info["wsgi_server"],
        "is_production": server_info["is_production"],
        "debug_mode": server_info["debug_mode"],
        "worker_pid": server_info["worker_pid"],
        "server_software": server_info["server_software"],
        "production_status": "🟢 PRODUCTION MODE" if server_info["is_production"] else "🟡 DEVELOPMENT MODE",
        # Kubernetes info
        "pod_name": env_info["kubernetes"]["pod_name"],
        "pod_namespace": env_info["kubernetes"]["pod_namespace"],
        "host_ip": env_info["kubernetes"]["host_ip"],
        # Application info
        "uptime": round(env_info["application"]["uptime"]),
        "python_version": env_info["application"]["python_version"],
        "platform": env_info["application"]["platform"],
        "architecture": env_info["application"]["architecture"],
        "pid": env_info["application"]["pid"],
        "ppid": env_info["application"]["ppid"],
        # System info
        "hostname": env_info["system"]["hostname"],
        "cpu_count": env_info["system"]["cpu_count"],
        "cpu_percent": env_info["system"]["cpu_percent"],
        "memory_total": env_info["system"]["memory_total_mb"],
        "memory_used": env_info["system"]["memory_used_mb"],
        "memory_available": env_info["system"]["memory_available_mb"],
        "memory_percent": env_info["system"]["memory_percent"],
        "load_avg": ", ".join(f"{x:.2f}" for x in env_info["system"]["load_avg"]),
        # Process info
        "num_threads": env_info["process"]["num_threads"],
        "process_memory": env_info["process"]["memory_percent"],
        "process_cpu": env_info["process"]["cpu_percent"],
        "create_time": env_info["process"]["create_time"],
        # Files
        "shared_files_list": "\n".join(f"<li>{file}</li>" for file in env_info["volumes"]["shared_files"]),
        "secret_files_list": "\n".join(f"<li>{file}</li>" for file in env_info["volumes"]["secret_store"]),
        # Environment variables
        "env_vars_list": "\n".join(
            f'<li><span class="label">{key}:</span><span class="value">{value}</span></li>'
            for key, value in env_info["environment_variables"].items()
        ),
    }

    # Simple template substitution
    html_content = html_template
    for key, value in template_vars.items():
        html_content = html_content.replace(f"{{{{ {key} }}}}", str(value))

    return html_content


@app.route("/api/env")
def api_env():
    """API endpoint for JSON environment data"""
    server_info = get_server_info()

    return jsonify(
        {
            "environment": os.environ.get("ENVIRONMENT", "unknown"),
            "bg_color": os.environ.get("BG_COLOR", "#1e3a8a"),
            "font_color": os.environ.get("FONT_COLOR", "#ffffff"),
            "server": server_info,
            "kubernetes": {
                "pod_name": os.environ.get("POD_NAME", "unknown"),
                "pod_namespace": os.environ.get("POD_NAMESPACE", "unknown"),
                "host_ip": os.environ.get("FROM_FIELD", "unknown"),
            },
            "uptime": round(time.time() - START_TIME, 2),
            "timestamp": datetime.now().isoformat(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        }
    )


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    # Update gauge metrics with current values
    try:
        process = psutil.Process()
        MEMORY_USAGE_GAUGE.set(process.memory_info().rss)
        CPU_USAGE_GAUGE.set(process.cpu_percent(interval=0.1))
        UPTIME_GAUGE.set(time.time() - START_TIME)
    except Exception as e:
        logger.warning(f"Error updating metrics: {e}")

    # Generate and return metrics in Prometheus format
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({"error": "Not Found", "path": request.path, "timestamp": datetime.now().isoformat()}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal Server Error", "message": str(error), "timestamp": datetime.now().isoformat()}), 500


def signal_handler(signum, frame):
    """Graceful shutdown handler"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    sys.exit(0)


# Production-ready application factory
def create_app():
    """Application factory for production deployment"""
    return app


if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    logger.info(f"🐍 Environment Display App (Flask) starting on port {port}")
    logger.info(f"📊 Environment: {os.environ.get('ENVIRONMENT', 'unknown')}")
    logger.info(f"🎨 Background Color: {os.environ.get('BG_COLOR', '#1e3a8a')}")
    logger.info(f"✏️ Font Color: {os.environ.get('FONT_COLOR', '#ffffff')}")
    logger.info(f"⏰ Started at: {datetime.now().isoformat()}")

    if is_production():
        logger.warning("⚠️  Using development server in production! Please use Gunicorn.")

    app.run(host="0.0.0.0", port=port, debug=debug)


# Middleware for request tracking
@app.before_request
def before_request():
    """Track request start time and increment active requests"""
    request.start_time = time.time()
    ACTIVE_REQUESTS.inc()


@app.after_request
def after_request(response):
    """Track request metrics after processing"""
    if hasattr(request, "start_time"):
        # Calculate request duration
        duration = time.time() - request.start_time
        endpoint = request.endpoint or "unknown"
        
        # Update metrics
        REQUEST_DURATION.labels(method=request.method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status=response.status_code
        ).inc()
    
    ACTIVE_REQUESTS.dec()
    return response
