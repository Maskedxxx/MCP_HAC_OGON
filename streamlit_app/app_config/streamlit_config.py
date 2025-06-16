# streamlit_app/config/streamlit_config.py
"""
Конфигурация для Streamlit приложения
"""

# Настройки страницы Streamlit
STREAMLIT_CONFIG = {
    "page_title": "🏠 AI Travel Assistant",
    "page_icon": "🏠",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Примеры запросов для демонстрации
EXAMPLE_QUERIES = [
    "Нужно жилье в Киеве на выходные для двоих",
    "Дешевое жилье до $50 в центре Лондона с собакой", 
    "Париж с 15 июля по 20 июля для семьи с ребенком",
    "Airbnb в Нью-Йорке рядом с Таймс Сквер недорого"
]

# Настройки анимации
ANIMATION_CONFIG = {
    "thinking_stages": [
        "🔍 Парсинг естественного языка...",
        "🧠 Извлечение параметров поиска...", 
        "⚙️ Подготовка запроса к Airbnb MCP...",
        "🔎 Выполнение поиска...",
        "✅ Анализ завершен!"
    ],
    "stage_delay": 0.3,  # секунд между этапами
    "auto_scroll_delay": 1000  # миллисекунд для auto-scroll
}

# Настройки отображения результатов
DISPLAY_CONFIG = {
    "max_results_options": ["Топ 5", "Топ 10", "Все результаты"],
    "sort_options": ["По умолчанию", "Цене", "Рейтингу"],
    "default_max_results": 5
}