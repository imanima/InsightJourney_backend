"""
Routes package for the API.

This package contains all the route modules for the API:
- auth: Authentication routes (login, register, logout)
- sessions: Session management and analysis routes
- analysis: Analysis routes for therapy sessions
"""

from .auth import router as auth_router
from .sessions import router as sessions_router
from .analysis import router as analysis_router

__all__ = ['auth_router', 'sessions_router', 'analysis_router']

# Routes should be organized by feature/resource:
# - auth.py (authentication routes)
# - sessions.py (session management routes)
# - users.py (user management routes)
# - analysis.py (direct analysis routes) 