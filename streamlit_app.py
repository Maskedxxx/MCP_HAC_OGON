# streamlit_app.py

import streamlit as st
import time
import pandas as pd
from airbnb import MCPClient as AirbnbClient, Formatter
from shared import AIAgent, ListingAnalyzer
from tripadvisor import Integrator

# Конфигурация страницы
st.set_page_config(
    page_title="🏠 AI Travel Assistant",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Кастомные стили для wow-эффекта
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
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}

.listing-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
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
</style>
""", unsafe_allow_html=True)


def init_state():
    """Инициализация состояния приложения"""
    if 'initialized' not in st.session_state:
        st.session_state.airbnb_client = AirbnbClient()
        st.session_state.formatter = Formatter()
        st.session_state.ai_agent = AIAgent()
        st.session_state.analyzer = ListingAnalyzer()
        st.session_state.integrator = Integrator()
        st.session_state.airbnb_started = False
        st.session_state.tripadvisor_started = False
        st.session_state.listings = []
        st.session_state.selected_index = None
        st.session_state.search_location = ""
        st.session_state.report = ""
        st.session_state.trip_report = ""
        st.session_state.extracted_params = {}
        st.session_state.current_query = ""
        st.session_state.current_listing_data = None
        st.session_state.initialized = True


def render_header():
    """Красивый заголовок приложения"""
    st.markdown("""
    <div class="main-header">
        <h1>🏠 AI Travel Assistant</h1>
        <p>Умный поиск жилья с интеграцией Airbnb + TripAdvisor через MCP протокол</p>
    </div>
    """, unsafe_allow_html=True)


def show_server_status():
    """Статус серверов в sidebar"""
    with st.sidebar:
        st.subheader("🖥️ Статус серверов")
        
        # Airbnb статус
        if st.session_state.airbnb_started:
            st.markdown('<p class="status-success">✅ Airbnb MCP: Активен</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Airbnb MCP: Остановлен</p>', unsafe_allow_html=True)
        
        # TripAdvisor статус
        if st.session_state.tripadvisor_started:
            st.markdown('<p class="status-success">✅ TripAdvisor MCP: Активен</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ TripAdvisor MCP: Остановлен</p>', unsafe_allow_html=True)
        
        # Кнопка остановки
        if st.button("🛑 Остановить все серверы", use_container_width=True):
            stop_servers()
            st.rerun()


def show_thinking_animation():
    """Анимация 'AI думает' с прогресс баром"""
    thinking_container = st.empty()
    progress_container = st.empty()
    
    with thinking_container.container():
        st.markdown("""
        <div class="thinking-animation">
            <h3>🤖 ИИ анализирует ваш запрос...</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Прогресс бар с этапами (более быстрая анимация)
    stages = [
        "🔍 Парсинг естественного языка...",
        "🧠 Извлечение параметров поиска...", 
        "⚙️ Подготовка запроса к Airbnb MCP...",
        "🔎 Выполнение поиска...",
        "✅ Анализ завершен!"
    ]
    
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()
    
    for i, stage in enumerate(stages):
        status_text.info(stage)
        progress_bar.progress((i + 1) / len(stages))
        time.sleep(0.3)  # Быстрее для более сдержанного эффекта
    
    thinking_container.empty()
    progress_container.empty()


def display_extracted_params(params_dict):
    """Красивое отображение извлеченных параметров"""
    if not params_dict:
        return
        
    st.subheader("🧠 Что понял ИИ из вашего запроса")
    
    # Создаем метрики в колонках
    cols = st.columns(4)
    
    metrics_data = [
        ("📍", "Локация", params_dict.get('location', '—')),
        ("👥", "Гостей", f"{params_dict.get('adults', '—')} взрослых"),
        ("📅", "Заезд", params_dict.get('checkin', '—')),
        ("📅", "Выезд", params_dict.get('checkout', '—')),
    ]
    
    for i, (emoji, label, value) in enumerate(metrics_data):
        with cols[i]:
            st.metric(f"{emoji} {label}", value)
    
    # Дополнительные параметры если есть
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


def display_search_results(listings):
    """Красивое отображение результатов поиска"""
    if not listings:
        st.error("😔 Жилье не найдено. Попробуйте изменить параметры поиска.")
        return
    
    st.subheader(f"🏠 Найдено {len(listings)} вариантов жилья")
    
    # Фильтры в expander
    with st.expander("🔧 Фильтры и сортировка", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_only = st.selectbox("Показать", ["Топ 5", "Топ 10", "Все результаты"])
        with col2:
            sort_by = st.selectbox("Сортировать по", ["По умолчанию", "Цене", "Рейтингу"])
        with col3:
            show_badges_only = st.checkbox("Только с наградами")
    
    # Определяем количество для показа
    max_results = {"Топ 5": 5, "Топ 10": 10, "Все результаты": len(listings)}[show_only]
    
    # Отображение карточек (компактный дизайн без фото)
    for idx, listing in enumerate(listings[:max_results]):
        name = listing["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"]
        price_details = listing["structuredDisplayPrice"]["explanationData"]["priceDetails"]
        rating_text = listing.get("avgRatingA11yLabel", "Нет рейтинга")
        badges = listing.get("badges", "")
        url = listing.get("url", "")
        
        # Извлекаем рейтинг
        if "out of 5" in rating_text:
            rating = rating_text.split(" ")[0]
            rating_display = f"⭐ {rating}/5"
        else:
            rating_display = "⭐ Новое"
        
        # Форматируем цену
        formatted_price = format_price(price_details)
        
        # Создаем компактную карточку
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"### {idx+1}. {name}")
                
                # Инфо строка
                info_parts = [rating_display, f"💰 {formatted_price}"]
                if badges:
                    info_parts.append(f"🏆 {badges}")
                
                st.markdown(" | ".join(info_parts))
                
                # Ссылка на Airbnb
                if url:
                    st.markdown(f"🔗 [Посмотреть на Airbnb]({url})")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Отступ
                if st.button("🔍 AI Анализ", key=f"analyze_{idx}", use_container_width=True):
                    perform_analysis(idx)
        
        st.divider()


def format_price(price_text):
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


def display_ai_analysis():
    """Отображение AI анализа и TripAdvisor данных"""
    if not st.session_state.report:
        return
    
    # Якорный контейнер для автоскроллинга
    analysis_anchor = st.empty()
    
    st.subheader("🤖 Детальный анализ жилья")
    
    # Вкладки для разных типов анализа
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 AI Анализ жилья", 
        "🍽️ Рестораны", 
        "🎭 Достопримечательности",
        "💬 Отзывы о районе",
        "🌍 Отчет о городе"
    ])
    
    with tab1:
        # AI отчет с красивым форматированием
        st.markdown("### 📋 Детальный отчет от ИИ")
        
        # Отображаем отчет в красивом контейнере
        with st.container():
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
                {st.session_state.report.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        render_tripadvisor_section("Рестораны рядом", "1", "🍽️")
    
    with tab3:
        render_tripadvisor_section("Достопримечательности рядом", "2", "🎭")
    
    with tab4:
        render_tripadvisor_section("Отзывы о районе", "4", "💬")
    
    with tab5:
        render_tripadvisor_section("Отчет о городе", "3", "🌍")


def render_tripadvisor_section(title, choice_code, emoji):
    """Рендер секции TripAdvisor"""
    st.markdown(f"### {emoji} {title}")
    
    if st.button(f"🌍 TripAdvisor: Получить {title.lower()}", key=f"trip_{choice_code}", use_container_width=True):
        start_tripadvisor()
        if st.session_state.tripadvisor_started:
            with st.spinner(f"🌍 Ищу {title.lower()} через TripAdvisor..."):
                result = st.session_state.integrator.process_additional_info_request(
                    choice_code, st.session_state.current_listing_data
                )
                if result:
                    st.session_state.trip_report = result
                    st.success("✅ Данные от TripAdvisor получены!")
                else:
                    st.error("❌ Не удалось получить данные")
    
    if st.session_state.trip_report:
        with st.container():
            st.markdown(f"""
            <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #28a745;">
                {st.session_state.trip_report.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)


def start_airbnb():
    """Запуск Airbnb сервера с индикацией"""
    if not st.session_state.airbnb_started:
        with st.spinner("🚀 Запускаю Airbnb MCP сервер..."):
            if st.session_state.airbnb_client.start_server():
                st.session_state.airbnb_started = True
                st.success("✅ Airbnb MCP сервер запущен!")
            else:
                st.error("❌ Не удалось запустить Airbnb сервер")


def start_tripadvisor():
    """Запуск TripAdvisor сервера с индикацией"""
    if not st.session_state.tripadvisor_started:
        with st.spinner("🌍 Запускаю TripAdvisor MCP сервер..."):
            if st.session_state.integrator.start_tripadvisor_service():
                st.session_state.tripadvisor_started = True
                st.success("✅ TripAdvisor MCP сервер запущен!")
            else:
                st.error("❌ Не удалось запустить TripAdvisor сервер")


def perform_search(query: str):
    """Выполнение поиска с AI анализом"""
    start_airbnb()
    if not st.session_state.airbnb_started:
        return
    
    # Анимация AI анализа
    show_thinking_animation()
    
    # AI анализ запроса
    try:
        tool_desc = st.session_state.ai_agent.get_search_function_description(
            st.session_state.airbnb_client
        )
        params = st.session_state.ai_agent.parse_user_request(query, tool_desc)
        
        st.session_state.extracted_params = params.model_dump(exclude_none=True)
        st.session_state.current_query = query
        
        # Поиск жилья
        with st.spinner("🔍 Выполняю поиск на Airbnb..."):
            search_args = params.model_dump(exclude_none=True)
            listings = st.session_state.airbnb_client.search_accommodations(**search_args)
        
        st.session_state.listings = listings
        st.session_state.search_location = params.location
        st.session_state.selected_index = None
        st.session_state.report = ""
        st.session_state.trip_report = ""
        st.session_state.current_listing_data = None
        
        if listings:
            st.success(f"✅ Найдено {len(listings)} вариантов жилья!")
        else:
            st.warning("⚠️ Жилье не найдено. Попробуйте изменить запрос.")
            
    except Exception as e:
        st.error(f"❌ Ошибка поиска: {str(e)}")


def perform_analysis(index: int):
    """Генерация AI отчета для выбранного жилья"""
    st.session_state.selected_index = index
    listing = st.session_state.listings[index]
    
    with st.spinner("🤖 Генерирую детальный AI отчет..."):
        try:
            data = st.session_state.analyzer.get_full_listing_data(
                listing,
                st.session_state.airbnb_client,
                st.session_state.search_location,
            )
            report = st.session_state.analyzer.generate_ai_report(
                data, st.session_state.current_query
            )
            st.session_state.report = report
            st.session_state.trip_report = ""
            st.session_state.current_listing_data = data
            
            # Более сдержанная анимация
            st.success("✅ AI анализ готов! Прокрутите вниз для просмотра отчета.")
            
            # Добавляем JavaScript для автоскроллинга к анализу
            st.markdown("""
            <script>
            setTimeout(function() {
                const analysisSection = document.querySelector('[data-testid="element-container"]:has([data-testid="stSubheader"]):has(text):last-of-type');
                if (analysisSection) {
                    analysisSection.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            }, 1000);
            </script>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Ошибка анализа: {str(e)}")


def stop_servers():
    """Остановка всех серверов"""
    if st.session_state.airbnb_started:
        st.session_state.airbnb_client.stop_server()
        st.session_state.airbnb_started = False
    if st.session_state.tripadvisor_started:
        st.session_state.integrator.stop_tripadvisor_service()
        st.session_state.tripadvisor_started = False
    st.success("✅ Все серверы остановлены")


# ====== ГЛАВНАЯ ФУНКЦИЯ ======
def main():
    """Главная функция приложения"""
    init_state()
    
    # Заголовок
    render_header()
    
    # Статус серверов в sidebar
    show_server_status()
    
    # Основной интерфейс
    st.markdown("### 💬 Опишите что вам нужно на обычном языке")
    
    # Примеры запросов
    with st.expander("💡 Примеры запросов", expanded=False):
        st.markdown("""
        - "Нужно жилье в Киеве на выходные для двоих"
        - "Дешевое жилье до $50 в центре Лондона с собакой"
        - "Париж с 15 июля по 20 июля для семьи с ребенком"
        - "Airbnb в Нью-Йорке рядом с Таймс Сквер"
        """)
    
    # Форма поиска
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "Ваш запрос:", 
            placeholder="Например: Нужно жилье в Париже на выходные для двоих",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("🔍 Найти", use_container_width=True, type="primary")
    
    # Выполнение поиска
    if search_button and user_query.strip():
        perform_search(user_query.strip())
    elif search_button:
        st.warning("⚠️ Введите запрос для поиска")
    
    # Отображение извлеченных параметров
    if st.session_state.extracted_params:
        st.markdown("---")
        display_extracted_params(st.session_state.extracted_params)
    
    # Отображение результатов поиска
    if st.session_state.listings:
        st.markdown("---")
        display_search_results(st.session_state.listings)
    
    # Отображение AI анализа
    if st.session_state.report:
        st.markdown("---")
        display_ai_analysis()


if __name__ == "__main__":
    main()