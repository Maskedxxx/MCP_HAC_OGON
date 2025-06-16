# streamlit_app/components/search_form.py
"""
Компонент формы поиска и отображения извлеченных параметров
"""

import streamlit as st
from app_config.streamlit_config import EXAMPLE_QUERIES


class SearchForm:
    """Компонент формы поиска"""
    
    def __init__(self):
        """Инициализация компонента"""
        pass
    
    def render(self) -> str:
        """
        Рендер формы поиска
        
        Returns:
            str: Введенный пользователем запрос или пустая строка
        """
        st.markdown("### 💬 Опишите что вам нужно на обычном языке")
        
        # Примеры запросов
        self._render_examples()
        
        # Форма поиска
        return self._render_search_input()
    
    def _render_examples(self):
        """Отображение примеров запросов"""
        with st.expander("💡 Примеры запросов", expanded=False):
            for example in EXAMPLE_QUERIES:
                st.markdown(f"- {example}")
    
    def _render_search_input(self) -> str:
        """
        Рендер поля ввода и кнопки поиска
        
        Returns:
            str: Запрос пользователя если нажата кнопка поиска
        """
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_query = st.text_input(
                "Ваш запрос:", 
                placeholder="Например: Нужно жилье в Париже на выходные для двоих",
                label_visibility="collapsed"
            )
        
        with col2:
            search_button = st.button("🔍 Найти", use_container_width=True, type="primary")
        
        # Обработка нажатия кнопки
        if search_button and user_query.strip():
            return user_query.strip()
        elif search_button:
            st.warning("⚠️ Введите запрос для поиска")
        
        return ""
    
    def display_extracted_params(self, params_dict: dict):
        """
        Красивое отображение извлеченных ИИ параметров
        
        Args:
            params_dict: Словарь с извлеченными параметрами
        """
        if not params_dict:
            return
        
        st.markdown("---")
        st.subheader("🧠 Что понял ИИ из вашего запроса")
        
        # Основные параметры в метриках
        self._render_main_params(params_dict)
        
        # Дополнительные параметры
        self._render_additional_params(params_dict)
    
    def _render_main_params(self, params_dict: dict):
        """Отображение основных параметров в метриках"""
        cols = st.columns(4)
        
        main_params = [
            ("📍", "Локация", params_dict.get('location', '—')),
            ("👥", "Гостей", f"{params_dict.get('adults', '—')} взрослых"),
            ("📅", "Заезд", params_dict.get('checkin', '—')),
            ("📅", "Выезд", params_dict.get('checkout', '—')),
        ]
        
        for i, (emoji, label, value) in enumerate(main_params):
            with cols[i]:
                st.metric(f"{emoji} {label}", value)
    
    def _render_additional_params(self, params_dict: dict):
        """Отображение дополнительных параметров"""
        additional_params = []
        
        if params_dict.get('children'):
            additional_params.append(f"👶 Дети: {params_dict['children']}")
        if params_dict.get('pets'):
            additional_params.append(f"🐕 Питомцы: {params_dict['pets']}")
        if params_dict.get('maxPrice'):
            additional_params.append(f"💰 Макс. цена: ${params_dict['maxPrice']}")
        if params_dict.get('minPrice'):
            additional_params.append(f"💸 Мин. цена: ${params_dict['minPrice']}")
        
        if additional_params:
            st.info(" | ".join(additional_params))