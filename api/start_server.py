#!/usr/bin/env python
"""
Startup script for FastAPI application on Render
"""
import os
import sys

def main():
    """Start the FastAPI application"""
    port = int(os.getenv('PORT', 8000))
    workers = int(os.getenv('WEB_CONCURRENCY', 1))
    
    # Run with uvicorn workers
    os.system(
        f"gunicorn main:app "
        f"--worker-class uvicorn.workers.UvicornWorker "
        f"--bind 0.0.0.0:{port} "
        f"--workers {workers} "
        f"--timeout 120 "
        f"--log-level info "
        f"--access-logfile - "
        f"--error-logfile -"
    )

if __name__ == "__main__":
    main()
