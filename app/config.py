LASTFM_API_KEY = ""

try:
    from local import *
except ImportError:
    raise SystemExit('local.py not found')