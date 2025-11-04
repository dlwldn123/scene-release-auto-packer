"""Flask extensions initialization."""

from __future__ import annotations

from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
