"""Flask extensions initialization."""

from __future__ import annotations

from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
