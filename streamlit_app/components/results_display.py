# streamlit_app/components/results_display.py
"""
Компонент отображения результатов поиска жилья
"""

import streamlit as st
from typing import List, Dict, Callable
from utils.ui_helpers import UIHelpers
from config.streamlit_config import DISPLAY_CONFIG


class ResultsDisplay:
    """Компонент для отображения результатов поиска"""
    
    def __init__(self):
        """Инициализация компонента"""
        self.ui_helpers = UIHelpers()
    
    def render(self, listings: List[Dict], perform_analysis_callback: Callable):
        """
        Рендер списка результатов поиска
        
        Args:
            listings: Список найденного жилья
            perform_analysis_callback: Функция для выполнения анализа
        """
        if not listings:
            st.error("😔 Жилье не найдено. Попробуйте изменить параметры поиска.")
            return
        
        st.markdown("---")
        st.subheader(f"🏠 Найдено {len(listings)} вариантов жилья")
        
        # Фильтры и настройки отображения
        max_results = self._render_filters()
        
        # Отображение карточек жилья
        self._render_listing_cards(listings[:max_results], perform_analysis_callback)
    
    def _render_filters(self) -> int:
        """
        Рендер фильтров и возврат максимального количества результатов
        
        Returns:
            int: Максимальное количество результатов для отображения
        """
        with st.expander("🔧 Фильтры и сортировка", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_only = st.selectbox(
                    "Показать", 
                    DISPLAY_CONFIG["max_results_options"]
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Сортировать по", 
                    DISPLAY_CONFIG["sort_options"]
                )
            
            with col3:
                show_badges_only = st.checkbox("Только с наградами")
        
        # Определяем количество для показа
        max_results_map = {
            "Топ 5": 5, 
            "Топ 10": 10, 
            "Все результаты": 1000  # Большое число для "всех"
        }
        
        return max_results_map.get(show_only, DISPLAY_CONFIG["default_max_results"])
    
    def _render_listing_cards(self, listings: List[Dict], perform_analysis_callback: Callable):
        """
        Рендер карточек жилья
        
        Args:
            listings: Список жилья для отображения
            perform_analysis_callback: Функция для анализа
        """
        for idx, listing in enumerate(listings):
            self._render_single_card(idx, listing, perform_analysis_callback)
            st.divider()
    
    def _render_single_card(self, idx: int, listing: Dict, perform_analysis_callback: Callable):
        """
        Рендер одной карточки жилья
        
        Args:
            idx: Индекс в списке
            listing: Данные о жилье
            perform_analysis_callback: Функция для анализа
        """
        # Извлечение данных
        name = listing["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"]
        price_details = listing["structuredDisplayPrice"]["explanationData"]["priceDetails"]
        rating_text = listing.get("avgRatingA11yLabel", "Нет рейтинга")
        badges = listing.get("badges", "")
        url = listing.get("url", "")
        
        # Форматирование данных
        formatted_price = self.ui_helpers.format_price(price_details)
        rating_display = self.ui_helpers.extract_rating(rating_text)
        
        # Создание карточки
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                self._render_card_content(idx, name, formatted_price, rating_display, badges, url)
            
            with col2:
                self._render_card_action(idx, perform_analysis_callback)
    
    def _render_card_content(self, idx: int, name: str, price: str, rating: str, badges: str, url: str):
        """Рендер содержимого карточки"""
        st.markdown(f"### {idx+1}. {name}")
        
        # Информационная строка
        info_parts = [rating, f"💰 {price}"]
        if badges:
            info_parts.append(f"🏆 {badges}")
        
        st.markdown(self.ui_helpers.create_info_metrics(info_parts))
        
        # Ссылка на Airbnb
        if url:
            st.markdown(f"🔗 [Посмотреть на Airbnb]({url})")
    
    def _render_card_action(self, idx: int, perform_analysis_callback: Callable):
        """Рендер кнопки действия в карточке"""
        st.markdown("<br>", unsafe_allow_html=True)  # Отступ
        if st.button("🔍 AI Анализ", key=f"analyze_{idx}", use_container_width=True):
            perform_analysis_callback(idx)