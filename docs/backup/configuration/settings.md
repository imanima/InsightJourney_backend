# System Settings

This document describes the system-wide settings in the Insight Journey platform.

## Environment Variables

Create a `.env` file in the root directory:

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# OpenAI Configuration
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

# CORS Configuration
CORS_ORIGINS=http://localhost:3000
CORS_METHODS=GET,POST,PUT,DELETE
CORS_HEADERS=Content-Type,Authorization

# Storage Configuration
UPLOAD_FOLDER=uploads
TRANSCRIPTS_FOLDER=transcripts
ANALYSIS_FOLDER=analysis

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=app.log

# Rate Limiting
RATELIMIT_DEFAULT=100/minute
RATELIMIT_STORAGE_URL=memory://

# Worker Configuration
WORKER_PROCESSES=4
WORKER_TIMEOUT=300
```

## Application Configuration

Configure application settings in `config/app.json`:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": true,
        "workers": 4,
        "timeout": 300
    },
    "security": {
        "password_policy": {
            "min_length": 8,
            "require_uppercase": true,
            "require_lowercase": true,
            "require_numbers": true,
            "require_special": true
        },
        "rate_limiting": {
            "default": "100/minute",
            "login": "5/minute",
            "register": "3/minute"
        },
        "cors": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "headers": ["Content-Type", "Authorization"]
        }
    },
    "database": {
        "sqlite": {
            "pool_size": 10,
            "max_overflow": 20,
            "timeout": 30
        },
        "neo4j": {
            "pool_size": 50,
            "connection_timeout": 5,
            "connection_acquisition_timeout": 60,
            "max_transaction_retry_time": 30
        }
    },
    "storage": {
        "uploads": {
            "allowed_extensions": ["txt", "pdf", "doc", "docx"],
            "max_size_mb": 10,
            "path": "uploads"
        },
        "transcripts": {
            "format": "json",
            "path": "transcripts"
        },
        "analysis": {
            "format": "json",
            "path": "analysis"
        }
    },
    "logging": {
        "version": 1,
        "disable_existing_loggers": false,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "default",
                "level": "DEBUG"
            }
        },
        "loggers": {
            "app": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": true
            }
        }
    },
    "cache": {
        "type": "redis",
        "url": "redis://localhost:6379/0",
        "default_timeout": 300
    },
    "queue": {
        "broker_url": "redis://localhost:6379/1",
        "result_backend": "redis://localhost:6379/2",
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "task_track_started": true,
        "task_time_limit": 3600
    }
}
```

## Logging Configuration

Configure logging in `config/logging.conf`:

```ini
[loggers]
keys=root,app

[handlers]
keys=console,file

[formatters]
keys=default

[logger_root]
level=INFO
handlers=console,file

[logger_app]
level=DEBUG
handlers=console,file
qualname=app
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=default
args=(sys.stdout,)

[handler_file]
class=FileHandler
level=DEBUG
formatter=default
args=('app.log',)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=
```

## Queue Configuration

Configure Celery in `config/celery.py`:

```python
from celery import Celery
from config import Config

celery = Celery(
    'insight_journey',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

celery.conf.update({
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'task_track_started': True,
    'task_time_limit': 3600,
    'worker_prefetch_multiplier': 1,
    'worker_max_tasks_per_child': 100,
    'broker_connection_retry_on_startup': True
})
```

## Cache Configuration

Configure Redis in `config/cache.py`:

```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})
```

## Example Usage

### Application Configuration

```python
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Configure logging
    configure_logging(app)
    
    return app

def configure_logging(app):
    import logging.config
    logging.config.fileConfig('config/logging.conf')
```

### Database Configuration

```python
from flask_sqlalchemy import SQLAlchemy
from neo4j import GraphDatabase

# SQLite configuration
db = SQLAlchemy()
db.create_all()

# Neo4j configuration
driver = GraphDatabase.driver(
    Config.NEO4J_URI,
    auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
    max_connection_pool_size=50,
    connection_timeout=5,
    max_transaction_retry_time=30
)
```

### Queue Configuration

```python
from celery import chain
from app.tasks import process_content, analyze_emotions, generate_insights

def start_analysis(session_id: str):
    workflow = chain(
        process_content.s(session_id),
        analyze_emotions.s(),
        generate_insights.s()
    )
    return workflow.apply_async()
```

### Cache Configuration

```python
from flask_caching import Cache
from functools import wraps

cache = Cache()

def cached(timeout=5 * 60, key_prefix='view/%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key_prefix % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator
```

### Security Configuration

```python
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# JWT configuration
jwt = JWTManager()

# CORS configuration
cors = CORS(
    resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": Config.CORS_METHODS,
            "allow_headers": Config.CORS_HEADERS
        }
    }
)
```

### Storage Configuration

```python
import os
from werkzeug.utils import secure_filename

def save_upload(file):
    filename = secure_filename(file.filename)
    allowed = filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    if not allowed:
        raise ValueError('File type not allowed')
    
    if file.content_length > Config.MAX_UPLOAD_SIZE:
        raise ValueError('File too large')
    
    path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(path)
    return path
``` 