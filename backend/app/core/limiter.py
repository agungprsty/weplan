from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory limiter; disabled in tests via conftest (limiter.enabled=False)
limiter = Limiter(key_func=get_remote_address, default_limits=[])
