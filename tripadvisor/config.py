# tripadvisor/config.py
"""
Конфигурация для TripAdvisor модуля
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройки TripAdvisor MCP сервера
TRIPADVISOR_CONFIG = {
    "api_key": os.getenv("TRIPADVISOR_API_KEY", ""),  # Вставьте ваш ключ
    "mcp_command": ["npx", "-y", "tripadvisor-mcp-node"],
    "default_language": "en",
    "search_radius": 50000,  # Радиус поиска в метрах
    "max_results": 10  # Максимум результатов для отображения
}

# Специфичные сообщения для TripAdvisor
MESSAGES = {
    "starting_server": "Запускаю TripAdvisor MCP сервер...",
    "server_stopped": "TripAdvisor сервер остановлен",
    "api_key_missing": "Не указан API ключ TripAdvisor",
    "server_error": "Ошибка запуска TripAdvisor сервера: {error}",
    "searching": "Ищу в TripAdvisor: {query}...",
    "searching_nearby": "Ищу рядом с координатами {lat}, {lon}..."
}