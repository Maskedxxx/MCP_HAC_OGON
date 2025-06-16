# streamlit_app/utils/session_manager.py
"""
Управление состоянием Streamlit сессии и клиентами MCP
"""

import streamlit as st
from airbnb import MCPClient as AirbnbClient, Formatter
from shared import AIAgent, ListingAnalyzer
from tripadvisor import Integrator
from .animations import show_thinking_animation


class SessionManager:
    """Менеджер состояния сессии и MCP клиентов"""
    
    def __init__(self):
        """Инициализация менеджера сессий"""
        self._init_session_state()
    
    def _init_session_state(self):
        """Инициализация состояния сессии если еще не создано"""
        if 'initialized' not in st.session_state:
            # Клиенты
            st.session_state.airbnb_client = AirbnbClient()
            st.session_state.formatter = Formatter()
            st.session_state.ai_agent = AIAgent()
            st.session_state.analyzer = ListingAnalyzer()
            st.session_state.integrator = Integrator()
            
            # Статусы серверов
            st.session_state.airbnb_started = False
            st.session_state.tripadvisor_started = False
            
            # Данные приложения
            st.session_state.listings = []
            st.session_state.selected_index = None
            st.session_state.search_location = ""
            st.session_state.report = ""
            
            # Разделенные TripAdvisor отчеты
            st.session_state.trip_restaurants = ""
            st.session_state.trip_attractions = ""
            st.session_state.trip_reviews = ""
            st.session_state.trip_city = ""
            
            st.session_state.extracted_params = {}
            st.session_state.current_query = ""
            st.session_state.current_listing_data = None
            
            st.session_state.initialized = True
    
    def show_server_status(self):
        """Отображение статуса серверов в sidebar"""
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
                self.stop_all_servers()
                st.rerun()
    
    def start_airbnb_server(self) -> bool:
        """Запуск Airbnb сервера"""
        if not st.session_state.airbnb_started:
            with st.spinner("🚀 Запускаю Airbnb MCP сервер..."):
                if st.session_state.airbnb_client.start_server():
                    st.session_state.airbnb_started = True
                    st.success("✅ Airbnb MCP сервер запущен!")
                    return True
                else:
                    st.error("❌ Не удалось запустить Airbnb сервер")
                    return False
        return True
    
    def start_tripadvisor_server(self) -> bool:
        """Запуск TripAdvisor сервера"""
        if not st.session_state.tripadvisor_started:
            with st.spinner("🌍 Запускаю TripAdvisor MCP сервер..."):
                if st.session_state.integrator.start_tripadvisor_service():
                    st.session_state.tripadvisor_started = True
                    st.success("✅ TripAdvisor MCP сервер запущен!")
                    return True
                else:
                    st.error("❌ Не удалось запустить TripAdvisor сервер")
                    return False
        return True
    
    def stop_all_servers(self):
        """Остановка всех серверов"""
        if st.session_state.airbnb_started:
            st.session_state.airbnb_client.stop_server()
            st.session_state.airbnb_started = False
        if st.session_state.tripadvisor_started:
            st.session_state.integrator.stop_tripadvisor_service()
            st.session_state.tripadvisor_started = False
        st.success("✅ Все серверы остановлены")
    
    def perform_search(self, query: str):
        """Выполнение поиска с AI анализом"""
        if not self.start_airbnb_server():
            return
        
        # Анимация AI анализа
        show_thinking_animation()
        
        try:
            # AI анализ запроса
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
            
            # Сохранение результатов
            st.session_state.listings = listings
            st.session_state.search_location = params.location
            st.session_state.selected_index = None
            st.session_state.report = ""
            
            # Очистка всех TripAdvisor отчетов
            st.session_state.trip_restaurants = ""
            st.session_state.trip_attractions = ""
            st.session_state.trip_reviews = ""
            st.session_state.trip_city = ""
            
            st.session_state.current_listing_data = None
            
            if listings:
                st.success(f"✅ Найдено {len(listings)} вариантов жилья!")
            else:
                st.warning("⚠️ Жилье не найдено. Попробуйте изменить запрос.")
                
        except Exception as e:
            st.error(f"❌ Ошибка поиска: {str(e)}")
    
    def perform_analysis(self, index: int):
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
                
                # Очистка всех TripAdvisor отчетов при новом анализе
                st.session_state.trip_restaurants = ""
                st.session_state.trip_attractions = ""
                st.session_state.trip_reviews = ""
                st.session_state.trip_city = ""
                
                st.session_state.current_listing_data = data
                
                # Сдержанная анимация
                st.success("✅ AI анализ готов! Прокрутите вниз для просмотра отчета.")
                
                # Auto-scroll к анализу
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
    
    def get_tripadvisor_data(self, choice_code: str) -> str:
        """Получение данных от TripAdvisor"""
        if not self.start_tripadvisor_server():
            return ""
        
        try:
            result = st.session_state.integrator.process_additional_info_request(
                choice_code, st.session_state.current_listing_data
            )
            
            # Сохраняем результат в соответствующее поле
            if choice_code == "1":  # Рестораны
                st.session_state.trip_restaurants = result or ""
            elif choice_code == "2":  # Достопримечательности
                st.session_state.trip_attractions = result or ""
            elif choice_code == "3":  # Город
                st.session_state.trip_city = result or ""
            elif choice_code == "4":  # Отзывы
                st.session_state.trip_reviews = result or ""
            
            return result or ""
        except Exception as e:
            st.error(f"❌ Ошибка TripAdvisor: {str(e)}")
            return ""
    
    def get_tripadvisor_report(self, report_type: str) -> str:
        """
        Получение конкретного TripAdvisor отчета
        
        Args:
            report_type: Тип отчета (restaurants, attractions, reviews, city)
            
        Returns:
            str: Содержимое отчета
        """
        report_map = {
            "restaurants": st.session_state.get('trip_restaurants', ''),
            "attractions": st.session_state.get('trip_attractions', ''),
            "reviews": st.session_state.get('trip_reviews', ''),
            "city": st.session_state.get('trip_city', '')
        }
        return report_map.get(report_type, '')