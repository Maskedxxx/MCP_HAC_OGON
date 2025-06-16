# streamlit_app/utils/ui_helpers.py
"""
Вспомогательные функции для UI и стили
"""

import streamlit as st


class UIHelpers:
    """Помощники для UI"""
    
    @staticmethod
    def load_custom_css():
        """Загрузка кастомных стилей"""
        st.markdown("""
        <style>
        /* Главный заголовок */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }

        /* Карточки параметров */
        .param-card {
            background: linear-gradient(145deg, #f8f9fa, #e9ecef);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        /* Карточки результатов */
        .listing-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border: 2px solid #e0e6ed;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .listing-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-color: #667eea;
        }

        /* Заголовки карточек */
        .card-title {
            background: linear-gradient(135deg, #17a2b8 0%, #769ba2 100%);
            color: white;
            padding: 0.8rem 1.2rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        }

        .card-title h4 {
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
        }

        /* Кнопки */
        .stButton > button {
            background: linear-gradient(145deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        /* Анимация загрузки */
        .thinking-animation {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(45deg, #f0f2ff, #faf0e6);
            border-radius: 15px;
            margin: 1rem 0;
        }

        /* Метрики */
        .metric-container {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            text-align: center;
        }

        /* Статусные индикаторы */
        .status-success {
            color: #28a745;
            font-weight: bold;
        }

        .status-error {
            color: #dc3545;
            font-weight: bold;
        }

        .status-info {
            color: #17a2b8;
            font-weight: bold;
        }

        /* Контейнеры для отчетов */
        .report-container {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 1rem 0;
        }

        .tripadvisor-container {
            background: #e8f5e8;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header():
        """Красивый заголовок приложения"""
        st.markdown("""
        <div class="main-header">
            <h1>🏠 AI Travel Assistant</h1>
            <p>Умный поиск жилья с интеграцией Airbnb + TripAdvisor через MCP протокол</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def format_price(price_text: str) -> str:
        """Форматирование цены из Airbnb"""
        if "x" in price_text and "nights:" in price_text:
            try:
                parts = price_text.split(":")
                left_part = parts[0]
                right_part = parts[1].strip()
                price_per_night = left_part.split("x")[0].strip().replace("$", "")
                nights = left_part.split("x")[1].strip().split()[0]
                total_price = right_part.replace("$", "").replace(",", "").strip()
                return f"${price_per_night}/ночь (${total_price} за {nights} ночей)"
            except:
                return price_text
        elif "x" in price_text:
            price_per_night = price_text.split("x")[0].strip().replace("$", "")
            return f"${price_per_night}/ночь"
        return price_text
    
    @staticmethod
    def extract_rating(rating_text: str) -> str:
        """Извлечение рейтинга из текста"""
        if "out of 5" in rating_text:
            return f"⭐ {rating_text.split(' ')[0]}/5"
        return "⭐ Новое"
    
    @staticmethod
    def create_info_metrics(info_parts: list) -> str:
        """Создание строки с метриками"""
        return " | ".join(info_parts)
    
    @staticmethod
    def render_report_container(content: str, container_type: str = "default"):
        """Рендер контейнера для отчетов с поддержкой Markdown"""
        if container_type == "ai":
            # Для AI отчетов используем прямой Markdown рендеринг без HTML контейнера
            with st.container():
                st.markdown(content)  # Прямой рендеринг Markdown
        else:
            # Для TripAdvisor отчетов оставляем как есть
            container_class = {
                "tripadvisor": "tripadvisor-container", 
                "default": "report-container"
            }.get(container_type, "report-container")
            
            st.markdown(f"""
            <div class="{container_class}">
                {content.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)