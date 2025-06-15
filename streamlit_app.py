import streamlit as st
from airbnb import MCPClient as AirbnbClient, Formatter
from shared import AIAgent, ListingAnalyzer
from tripadvisor import Integrator

st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="🏠",
    layout="wide",
)


def init_state():
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


def start_airbnb():
    if not st.session_state.airbnb_started:
        if st.session_state.airbnb_client.start_server():
            st.session_state.airbnb_started = True
        else:
            st.error("Не удалось запустить сервер Airbnb")


def start_tripadvisor():
    if not st.session_state.tripadvisor_started:
        if st.session_state.integrator.start_tripadvisor_service():
            st.session_state.tripadvisor_started = True
        else:
            st.error("Не удалось запустить TripAdvisor сервис")


def perform_search(query: str):
    """Run AI-assisted search and store results in session."""
    start_airbnb()
    if not st.session_state.airbnb_started:
        return
    with st.spinner("🤖 AI анализирует запрос..."):
        tool_desc = st.session_state.ai_agent.get_search_function_description(
            st.session_state.airbnb_client
        )
        params = st.session_state.ai_agent.parse_user_request(query, tool_desc)

    st.session_state.extracted_params = params.model_dump(exclude_none=True)
    st.session_state.current_query = query

    with st.spinner("🔍 Выполняю поиск на Airbnb..."):
        search_args = params.model_dump(exclude_none=True)
        listings = st.session_state.airbnb_client.search_accommodations(**search_args)

    st.session_state.listings = listings
    st.session_state.search_location = params.location
    st.session_state.selected_index = None
    st.session_state.report = ""
    st.session_state.trip_report = ""
    st.session_state.current_listing_data = None


def perform_analysis(index: int):
    """Generate AI report for selected listing."""
    st.session_state.selected_index = index
    listing = st.session_state.listings[index]
    with st.spinner("🤖 Генерирую отчет по жилью..."):
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


def stop_servers():
    if st.session_state.airbnb_started:
        st.session_state.airbnb_client.stop_server()
        st.session_state.airbnb_started = False
    if st.session_state.tripadvisor_started:
        st.session_state.integrator.stop_tripadvisor_service()
        st.session_state.tripadvisor_started = False


init_state()

st.title("🏠 AI Travel Assistant")

user_query = st.text_input("Введите ваш запрос")

col1, col2 = st.columns(2)
with col1:
    if st.button("Поиск"):
        perform_search(user_query)
with col2:
    if st.button("Остановить сервера"):
        stop_servers()

if st.session_state.extracted_params:
    with st.expander("Извлеченные параметры", expanded=False):
        for key, value in st.session_state.extracted_params.items():
            st.write(f"**{key}**: {value}")

if st.session_state.listings:
    st.subheader("Результаты поиска")
    for idx, l in enumerate(st.session_state.listings[:5]):
        name = l["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"]
        price = l["structuredDisplayPrice"]["explanationData"]["priceDetails"]
        rating = l.get("avgRatingA11yLabel", "Нет рейтинга")
        url = l.get("url", "")
        with st.container(border=True):
            st.markdown(f"**{idx+1}. {name}**")
            st.markdown(f"{price} | {rating}")
            if url:
                st.markdown(f"[Ссылка на Airbnb]({url})")
            if st.button("Детальный анализ", key=f"analyze_{idx}"):
                perform_analysis(idx)

if st.session_state.report:
    tab_ai, tab_trip = st.tabs(["AI Анализ", "TripAdvisor"])
    with tab_ai:
        st.text(st.session_state.report)
    with tab_trip:
        trip_option = st.selectbox(
            "Тип информации",
            ["-", "Рестораны рядом", "Достопримечательности рядом", "Информация о городе", "Отзывы о районе"],
            key="trip_option",
        )
        if st.button("Получить данные", key="get_trip") and trip_option != "-":
            start_tripadvisor()
            choice_map = {
                "Рестораны рядом": "1",
                "Достопримечательности рядом": "2",
                "Информация о городе": "3",
                "Отзывы о районе": "4",
            }
            result = st.session_state.integrator.process_additional_info_request(
                choice_map[trip_option], st.session_state.current_listing_data
            )
            st.session_state.trip_report = result

        if st.session_state.trip_report:
            st.text(st.session_state.trip_report)

