# config.py
"""
Общие настройки для всего приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройки OpenAI
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "model": "gpt-4.1",
    "max_tokens": 3000,
    "temperature": 0
}

# Эмодзи для вывода
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
    "ai": "🤖",
    "robot": "🤖",
    "user": "👤",
    "brain": "🧠",
    "select": "👉",
    "back": "↩️",
    "question": "❓",
    "location": "📍",
    "restaurant": "🍽️",
    "attraction": "🎭",
    "review": "💬",
    "photo": "📸",
    "tripadvisor": "🌍"
}

# Общие сообщения
MESSAGES = {
    # Общие
    "server_error": "Ошибка запуска сервера: {error}",
    "search_error": "Ошибка поиска",
    "search_failed": "Поиск не удался: {error}",
    
    # ИИ агент
    "getting_function_description": "Получаю описание функций от MCP сервера...",
    "parsing_request": "ИИ анализирует ваш запрос...",
    "ai_extracted_params": "ИИ извлек следующие параметры",
    "ai_error": "Ошибка ИИ обработки: {error}",
    "user_request": "Запрос пользователя",
    
    # Интерактивный поиск
    "interactive_title": "🎯 ИНТЕРАКТИВНЫЙ ПОИСК ЖИЛЬЯ С ИИ",
    "interactive_help": "Опишите что вам нужно на обычном языке!",
    "interactive_examples": "Примеры: 'Киев на выходные для двоих', 'Лондон дешево с собакой'",
    "interactive_exit": "Введите 'выход' для завершения",
    "interactive_analyze_prompt": "Хотите детальный ИИ анализ какого-то варианта? (y/n): ",
    
    # Анализ
    "tripadvisor_analysis": "ИИ анализ данных TripAdvisor",
    "additional_info_menu": "Дополнительная информация о местности"
}