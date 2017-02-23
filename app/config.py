LASTFM_API_KEY = ""

try:
    from app.local import *
except ImportError:
    raise SystemExit('local.py not found')