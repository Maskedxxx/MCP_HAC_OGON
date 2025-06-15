# airbnb/config.py
"""
Конфигурация для Airbnb модуля
"""

# Настройки MCP сервера
MCP_SERVER_COMMAND = ["npx", "-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"]
SERVER_STARTUP_TIMEOUT = 10  # секунд

# Настройки поиска по умолчанию
DEFAULT_SEARCH_PARAMS = {
    "adults": 2,
    "children": 0,
    "infants": 0,
    "pets": 0
}

# Настройки отображения
DISPLAY_CONFIG = {
    "max_results_to_show": 10,
    "max_amenities_to_show": 10,
    "show_badges": True,
    "show_rating": True,
    "show_price": True,
    "show_url": True
}

# Специфичные сообщения для Airbnb
MESSAGES = {
    "starting_server": "Запускаю Airbnb MCP сервер...",
    "server_stopped": "Сервер остановлен",
    "searching": "Ищу жилье в {location} для {adults} человек...",
    "found_results": "НАЙДЕНО {count} ВАРИАНТОВ ЖИЛЬЯ:",
    "no_results": "Жилье не найдено",
    "getting_details": "Получаю детали листинга {listing_id}..."
}