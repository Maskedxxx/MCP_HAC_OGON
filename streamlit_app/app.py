# streamlit_app/app.py
"""
Главный файл Streamlit приложения для AI Travel Assistant
"""

import streamlit as st
import sys
import os

# Добавляем корневую папку в путь для импорта основных модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import SearchForm, ResultsDisplay, AIAnalysis, TripAdvisorTabs
from utils import SessionManager, UIHelpers
from app_config.streamlit_config import STREAMLIT_CONFIG

# Конфигурация страницы
st.set_page_config(**STREAMLIT_CONFIG)


def main():
    """Главная функция приложения"""
    # Инициализация
    session_manager = SessionManager()
    ui_helpers = UIHelpers()
    
    # Загрузка стилей и заголовка
    ui_helpers.load_custom_css()
    ui_helpers.render_header()
    
    # Статус серверов в sidebar
    session_manager.show_server_status()
    
    # Компоненты интерфейса
    search_form = SearchForm()
    results_display = ResultsDisplay()
    ai_analysis = AIAnalysis()
    
    # Основной интерфейс
    render_main_interface(session_manager, search_form, results_display, ai_analysis)


def render_main_interface(session_manager, search_form, results_display, ai_analysis):
    """Рендер основного интерфейса"""
    
    # Форма поиска
    user_query = search_form.render()
    
    # Обработка поиска
    if user_query:
        session_manager.perform_search(user_query)
    
    # Отображение результатов
    if st.session_state.get('extracted_params'):
        search_form.display_extracted_params(st.session_state.extracted_params)
    
    if st.session_state.get('listings'):
        results_display.render(st.session_state.listings, session_manager.perform_analysis)
    
    # AI анализ и TripAdvisor
    if st.session_state.get('report'):
        ai_analysis.render()


if __name__ == "__main__":
    main()