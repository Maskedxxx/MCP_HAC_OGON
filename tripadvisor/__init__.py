# tripadvisor/__init__.py
"""
Модуль для работы с TripAdvisor MCP сервером
"""

from .client import MCPClient
from .integrator import Integrator

__all__ = ['MCPClient', 'Integrator']