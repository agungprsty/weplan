from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory limiter; ketat 5/min login, 3/min forgot (P1)
limiter = Limiter(key_func=get_remote_address, default_limits=[])
