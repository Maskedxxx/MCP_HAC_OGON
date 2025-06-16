# streamlit_app/components/tripadvisor_tabs.py
"""
Компонент вкладок TripAdvisor для дополнительной информации
"""

import streamlit as st
from utils.ui_helpers import UIHelpers
from utils.animations import show_success_message, show_error_message


class TripAdvisorTabs:
    """Компонент для TripAdvisor вкладок"""
    
    def __init__(self):
        """Инициализация компонента"""
        self.ui_helpers = UIHelpers()
    
    def render_restaurants_tab(self):
        """Рендер вкладки ресторанов"""
        self._render_tripadvisor_section(
            title="Рестораны рядом",
            choice_code="1",
            emoji="🍽️",
            description="Найти лучшие рестораны в окрестностях жилья"
        )
    
    def render_attractions_tab(self):
        """Рендер вкладки достопримечательностей"""
        self._render_tripadvisor_section(
            title="Достопримечательности рядом",
            choice_code="2", 
            emoji="🎭",
            description="Найти интересные места и достопримечательности поблизости"
        )
    
    def render_reviews_tab(self):
        """Рендер вкладки отзывов о районе"""
        self._render_tripadvisor_section(
            title="Отзывы о районе",
            choice_code="4",
            emoji="💬", 
            description="Собрать отзывы туристов о районе расположения жилья"
        )
    
    def render_city_tab(self):
        """Рендер вкладки отчета о городе"""
        self._render_tripadvisor_section(
            title="Отчет о городе",
            choice_code="3",
            emoji="🌍",
            description="Получить общую информацию о городе и его достопримечательностях"
        )
    
    def _render_tripadvisor_section(self, title: str, choice_code: str, emoji: str, description: str):
        """
        Универсальный рендер секции TripAdvisor
        
        Args:
            title: Заголовок секции
            choice_code: Код для API запроса
            emoji: Эмодзи для кнопки
            description: Описание функции
        """
        st.markdown(f"### {emoji} {title}")
        st.markdown(f"*{description}*")
        
        # Кнопка получения данных
        button_key = f"trip_{choice_code}"
        button_text = f"🌍 TripAdvisor: Получить {title.lower()}"
        
        if st.button(button_text, key=button_key, use_container_width=True):
            self._handle_tripadvisor_request(choice_code, title)
        
        # Отображение результатов
        self._display_tripadvisor_results()
    
    def _handle_tripadvisor_request(self, choice_code: str, title: str):
        """
        Обработка запроса к TripAdvisor
        
        Args:
            choice_code: Код запроса
            title: Название для сообщений
        """
        # Проверка наличия данных о жилье
        if not st.session_state.get('current_listing_data'):
            show_error_message("Сначала выберите жилье для анализа")
            return
        
        # Запуск TripAdvisor сервера
        session_manager = self._get_session_manager()
        if not session_manager.start_tripadvisor_server():
            return
        
        # Получение данных
        with st.spinner(f"🌍 Ищу {title.lower()} через TripAdvisor..."):
            result = session_manager.get_tripadvisor_data(choice_code)
            
            if result:
                st.session_state.trip_report = result
                show_success_message("Данные от TripAdvisor получены!")
            else:
                show_error_message("Не удалось получить данные от TripAdvisor")
    
    def _display_tripadvisor_results(self):
        """Отображение результатов от TripAdvisor"""
        if st.session_state.get('trip_report'):
            # Отображение в красивом контейнере
            self.ui_helpers.render_report_container(
                st.session_state.trip_report, 
                "tripadvisor"
            )
    
    def _get_session_manager(self):
        """
        Получение экземпляра SessionManager
        
        Returns:
            SessionManager: Экземпляр менеджера сессий
        """
        # Импорт здесь для избежания циклических импортов
        from utils.session_manager import SessionManager
        return SessionManager()