# streamlit_app/components/ai_analysis.py
"""
Компонент AI анализа жилья и интеграции с TripAdvisor
"""

import streamlit as st
import pandas as pd
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
            "🌍 Отчет о городе",
            "🗺️ Карта"
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
        
        with tabs[5]:
            self._render_map_tab()
    
    def _render_ai_report(self):
        """Рендер AI отчета о жилье"""
        st.markdown("### 📋 Детальный отчет от ИИ")
        
        # Отображение отчета с поддержкой Markdown
        report_content = st.session_state.report
        self.ui_helpers.render_report_container(report_content, "ai")
    
    def _render_map_tab(self):
        """Рендер вкладки с картой"""
        if not st.session_state.get('current_listing_data'):
            st.info("📍 Сначала выберите жилье для отображения на карте")
            return
        
        coordinates = st.session_state.current_listing_data["basic"]["coordinates"]
        lat, lon = coordinates["latitude"], coordinates["longitude"]
        listing_name = st.session_state.current_listing_data["basic"]["name"]
        
        st.markdown("### 🗺️ Расположение жилья")
        st.markdown(f"**📍 {listing_name}**")
        
        # Создание DataFrame для карты
        map_data = pd.DataFrame({
            'lat': [lat],
            'lon': [lon],
            'size': [20]
        })
        
        # Отображение карты
        st.map(map_data, size='size')
        
        # Дополнительная информация
        st.markdown(f"""
        **Координаты:** {lat:.6f}, {lon:.6f}
        
        💡 *Tip: Используйте другие вкладки для поиска ресторанов и достопримечательностей рядом с этим местом.*
        """)