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
            description="Найти лучшие рестораны в окрестностях жилья",
            report_type="restaurants"
        )
    
    def render_attractions_tab(self):
        """Рендер вкладки достопримечательностей"""
        self._render_tripadvisor_section(
            title="Достопримечательности рядом",
            choice_code="2", 
            emoji="🎭",
            description="Найти интересные места и достопримечательности поблизости",
            report_type="attractions"
        )
    
    def render_reviews_tab(self):
        """Рендер вкладки отзывов о районе"""
        self._render_tripadvisor_section(
            title="Отзывы о районе",
            choice_code="4",
            emoji="💬", 
            description="Собрать отзывы туристов о районе расположения жилья",
            report_type="reviews"
        )
    
    def render_city_tab(self):
        """Рендер вкладки отчета о городе"""
        self._render_tripadvisor_section(
            title="Отчет о городе",
            choice_code="3",
            emoji="🌍",
            description="Получить общую информацию о городе и его достопримечательностях",
            report_type="city"
        )
    
    def _render_tripadvisor_section(self, title: str, choice_code: str, emoji: str, description: str, report_type: str):
        """
        Универсальный рендер секции TripAdvisor
        
        Args:
            title: Заголовок секции
            choice_code: Код для API запроса
            emoji: Эмодзи для кнопки
            description: Описание функции
            report_type: Тип отчета для получения из состояния
        """
        st.markdown(f"### {emoji} {title}")
        st.markdown(f"*{description}*")
        
        # Кнопка получения данных
        button_key = f"trip_{choice_code}"
        button_text = f"🌍 TripAdvisor: Получить {title.lower()}"
        
        if st.button(button_text, key=button_key, use_container_width=True):
            self._handle_tripadvisor_request(choice_code, title)
        
        # Отображение результатов для конкретного типа
        self._display_tripadvisor_results(report_type)
    
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
        
        # Запуск TripAdvisor сервера и получение данных
        session_manager = self._get_session_manager()
        
        with st.spinner(f"🌍 Ищу {title.lower()} через TripAdvisor..."):
            result = session_manager.get_tripadvisor_data(choice_code)
            
            if result:
                show_success_message("Данные от TripAdvisor получены!")
            else:
                show_error_message("Не удалось получить данные от TripAdvisor")
    
    def _display_tripadvisor_results(self, report_type: str):
        """
        Отображение результатов от TripAdvisor для конкретного типа
        
        Args:
            report_type: Тип отчета (restaurants, attractions, reviews, city)
        """
        session_manager = self._get_session_manager()
        report_content = session_manager.get_tripadvisor_report(report_type)
        
        if report_content:
            # Отображение в красивом контейнере
            self.ui_helpers.render_report_container(
                report_content, 
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