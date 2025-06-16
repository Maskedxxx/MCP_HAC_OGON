# streamlit_app/components/results_display.py
"""
Компонент отображения результатов поиска жилья
"""

import streamlit as st
import re
from typing import List, Dict, Callable
from utils.ui_helpers import UIHelpers
from app_config.streamlit_config import DISPLAY_CONFIG


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
        max_results, sort_by = self._render_filters()
        
        # Применение сортировки
        sorted_listings = self._apply_sorting(listings, sort_by)
        
        # Отображение карточек жилья
        self._render_listing_cards(sorted_listings[:max_results], perform_analysis_callback)
    
    def _render_filters(self) -> tuple:
        """
        Рендер фильтров и возврат параметров отображения
        
        Returns:
            tuple: (max_results: int, sort_by: str)
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
        
        max_results = max_results_map.get(show_only, DISPLAY_CONFIG["default_max_results"])
        return max_results, sort_by
    
    def _apply_sorting(self, listings: List[Dict], sort_by: str) -> List[Dict]:
        """
        Применение сортировки к списку жилья
        
        Args:
            listings: Исходный список
            sort_by: Тип сортировки
            
        Returns:
            List[Dict]: Отсортированный список
        """
        if sort_by == "Цене":
            return sorted(listings, key=self._extract_price_for_sorting)
        elif sort_by == "Рейтингу":
            return sorted(listings, key=self._extract_rating_for_sorting, reverse=True)
        else:
            return listings  # По умолчанию
    
    def _extract_price_for_sorting(self, listing: Dict) -> float:
        """Извлечение цены для сортировки"""
        try:
            price_details = listing["structuredDisplayPrice"]["explanationData"]["priceDetails"]
            # Извлекаем первое число из строки цены
            price_match = re.search(r'\$(\d+)', price_details)
            return float(price_match.group(1)) if price_match else 999999
        except:
            return 999999  # Высокая цена для проблемных записей
    
    def _extract_rating_for_sorting(self, listing: Dict) -> float:
        """Извлечение рейтинга для сортировки"""
        try:
            rating_text = listing.get("avgRatingA11yLabel", "0")
            if "out of 5" in rating_text:
                return float(rating_text.split(" ")[0])
            return 0.0  # Для новых без рейтинга
        except:
            return 0.0
    
    def _render_listing_cards(self, listings: List[Dict], perform_analysis_callback: Callable):
        """
        Рендер карточек жилья
        
        Args:
            listings: Список жилья для отображения
            perform_analysis_callback: Функция для анализа
        """
        for idx, listing in enumerate(listings):
            self._render_single_card(idx, listing, perform_analysis_callback)
            # Добавляем разделитель между карточками
            if idx < len(listings) - 1:  # Не добавляем divider после последней карточки
                st.markdown("<br>", unsafe_allow_html=True)
    
    def _render_single_card(self, idx: int, listing: Dict, perform_analysis_callback: Callable):
        """
        Рендер одной карточки жилья с красивым дизайном
        
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
        
        # Создание красивой карточки
        # st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            self._render_card_content(idx, name, formatted_price, rating_display, badges, url)
        
        with col2:
            self._render_card_action(idx, perform_analysis_callback)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_card_content(self, idx: int, name: str, price: str, rating: str, badges: str, url: str):
        """Рендер содержимого карточки с красивым заголовком"""
        
        # Красивый заголовок с CSS классом
        st.markdown(f"""
        <div class="card-title">
            <h4>{idx+1}. {name}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Информационная строка
        info_parts = [rating, f"💰 {price}"]
        if badges:
            info_parts.append(f"🏆 {badges}")
        
        st.markdown(f"**{self.ui_helpers.create_info_metrics(info_parts)}**")
        
        # Ссылка на Airbnb
        if url:
            st.markdown(f"🔗 [Посмотреть на Airbnb]({url})")
    
    def _render_card_action(self, idx: int, perform_analysis_callback: Callable):
        """Рендер кнопки действия в карточке"""
        st.markdown("<br>", unsafe_allow_html=True)  # Отступ
        if st.button("🔍 AI Анализ", key=f"analyze_{idx}", use_container_width=True):
            perform_analysis_callback(idx)