import os
import dotenv

dotenv.load_dotenv(".env")

# Basic setup
bind = f"0.0.0.0:{os.environ.get('APP_PORT')}"
workers = 4
timeout = 30
worker_tmp_dir = "/dev/shm"
worker_class = "gthread"
threads = 4

# Log information
os.makedirs("logs/gunicorn", exist_ok=True)
errorlog = accesslog = "logs/gunicorn/dev.log"
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'"
