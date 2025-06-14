# config.py
"""
Конфигурация для Airbnb MCP клиента
"""

# Настройки MCP сервера
MCP_SERVER_COMMAND = ["npx", "-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"]
SERVER_STARTUP_TIMEOUT = 5  # секунд

# Настройки поиска по умолчанию
DEFAULT_SEARCH_PARAMS = {
    "adults": 2,
    "children": 0,
    "infants": 0,
    "pets": 0
}

# Настройки OpenAI
OPENAI_CONFIG = {
    "model": "gpt-4.1",  # Используем более доступную модель
    "max_tokens": 3000,
    "temperature": 0 # Низкая температура для точности извлечения параметров
}

# Настройки отображения
DISPLAY_CONFIG = {
    "max_results_to_show": 10,  # Сколько результатов показывать
    "max_amenities_to_show": 10,  # Сколько удобств показывать
    "show_badges": True,  # Показывать ли значки (Guest favorite и т.д.)
    "show_rating": True,  # Показывать ли рейтинг
    "show_price": True,  # Показывать ли цену
    "show_url": True  # Показывать ли URL
}

# Эмодзи для вывода (можно легко настроить)
EMOJIS = {
    "start": "🚀",
    "success": "✅", 
    "error": "❌",
    "search": "🔍",
    "house": "🏠",
    "star": "⭐",
    "money": "💰",
    "trophy": "🏆",
    "link": "🔗",
    "details": "📋",
    "stop": "🛑",
    "finish": "🎉",
    "ai": "🤖",        # Для ИИ обработки
    "robot": "🤖",      # Для отображения результатов ИИ
    "user": "👤",       # Для запросов пользователя
    "brain": "🧠",      # Для анализа
    "select": "👉",     # Для выбора вариантов
    "back": "↩️",       # Назад
    "question": "❓"    # Вопросы пользователю
}

# Языковые настройки
MESSAGES = {
    "starting_server": "Запускаю Airbnb MCP сервер...",
    "server_stopped": "Сервер остановлен",
    "searching": "Ищу жилье в {location} для {adults} человек...",
    "found_results": "НАЙДЕНО {count} ВАРИАНТОВ ЖИЛЬЯ:",
    "no_results": "Жилье не найдено",
    "getting_details": "Получаю детали листинга {listing_id}...",
    "search_error": "Ошибка поиска",
    "server_error": "Ошибка запуска сервера: {error}",
    
    # Новые сообщения для ИИ агента
    "getting_function_description": "Получаю описание функций от MCP сервера...",
    "parsing_request": "ИИ анализирует ваш запрос...",
    "ai_extracted_params": "ИИ извлек следующие параметры",
    "ai_error": "Ошибка ИИ обработки: {error}",
    "search_failed": "Поиск не удался: {error}",
    "user_request": "Запрос пользователя",
    "ai_demo_start": "🤖 ДЕМОНСТРАЦИЯ ИИ АГЕНТА ДЛЯ ПОИСКА ЖИЛЬЯ"
}