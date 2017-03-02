LASTFM_API_KEY = ''
GENIUS_BEARER_TOKEN = ''

try:
    from local import *
except ImportError:
    raise SystemExit('local.py not found')