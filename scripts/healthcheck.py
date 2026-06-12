#!/usr/bin/env python3
import requests
import sys
import os
import psycopg2
import redis

def check_api():
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200:
            print("API: OK")
            return True
    except Exception as e:
        print(f"API: FAIL ({e})")
    return False

def check_database():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://teos:teos_pass@localhost:5432/teos_db"))
        conn.close()
        print("DB: OK")
        return True
    except Exception as e:
        print(f"DB: FAIL ({e})")
    return False

def check_redis():
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        print("Redis: OK")
        return True
    except Exception as e:
        print(f"Redis: FAIL ({e})")
    return False

if __name__ == "__main__":
    ok = check_api() and check_database() and check_redis()
    sys.exit(0 if ok else 1)
