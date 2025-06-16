# streamlit_app/components/ai_analysis.py
"""
Компонент AI анализа жилья и интеграции с TripAdvisor
"""

import streamlit as st
from utils.ui_helpers import UIHelpers
from .tripadvisor_tabs import TripAdvisorTabs


class AIAnalysis:
    """Компонент для отображения AI анализа"""
    
    def __init__(self):
        """Инициализация компонента"""
        self.ui_helpers = UIHelpers()
        self.tripadvisor_tabs = TripAdvisorTabs()
    
    def render(self):
        """Основной рендер AI анализа"""
        if not st.session_state.get('report'):
            return
        
        st.markdown("---")
        st.subheader("🤖 Детальный анализ жилья")
        
        # Создание вкладок
        tabs = st.tabs([
            "🏠 AI Анализ жилья", 
            "🍽️ Рестораны", 
            "🎭 Достопримечательности",
            "💬 Отзывы о районе",
            "🌍 Отчет о городе"
        ])
        
        # Рендер содержимого вкладок
        with tabs[0]:
            self._render_ai_report()
        
        with tabs[1]:
            self.tripadvisor_tabs.render_restaurants_tab()
        
        with tabs[2]:
            self.tripadvisor_tabs.render_attractions_tab()
        
        with tabs[3]:
            self.tripadvisor_tabs.render_reviews_tab()
        
        with tabs[4]:
            self.tripadvisor_tabs.render_city_tab()
    
    def _render_ai_report(self):
        """Рендер AI отчета о жилье"""
        st.markdown("### 📋 Детальный отчет от ИИ")
        
        # Отображение отчета в красивом контейнере
        report_content = st.session_state.report
        self.ui_helpers.render_report_container(report_content, "ai")