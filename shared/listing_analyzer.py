# shared/listing_analyzer.py
"""
Модуль для детального анализа жилья с помощью ИИ
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import OPENAI_CONFIG, EMOJIS


class ListingAnalyzer:
    """ИИ анализатор для создания детальных отчетов по жилью"""
    
    def __init__(self, api_key: str = None):
        """
        Инициализация анализатора
        
        Args:
            api_key: API ключ OpenAI
        """
        self.api_key = api_key or OPENAI_CONFIG["api_key"]
        self.client = OpenAI(api_key=self.api_key)
        self.model = OPENAI_CONFIG["model"]
    
    def select_listing_interactive(self, listings: List[Dict]) -> Optional[Dict]:
        """
        Интерактивный выбор жилья пользователем
        
        Args:
            listings: Список найденного жилья
            
        Returns:
            Dict: Выбранное жилье или None
        """
        if not listings:
            print(f"{EMOJIS['error']} Нет вариантов для анализа")
            return None
        
        print(f"\n{EMOJIS['brain']} ВЫБЕРИТЕ ЖИЛЬЕ ДЛЯ ДЕТАЛЬНОГО АНАЛИЗА:")
        print("="*60)
        
        # Показываем краткий список
        for i, listing in enumerate(listings[:10], 1):
            name = listing["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"]
            price_details = listing["structuredDisplayPrice"]["explanationData"]["priceDetails"]
            print(f"{i:2d}. {name[:50]}{'...' if len(name) > 50 else ''}")
            print(f"    💰 {price_details}")
        
        print(f"\n0. {EMOJIS['back']} Вернуться к поиску")
        
        while True:
            try:
                choice = input(f"\n{EMOJIS['select']} Введите номер (0-{min(len(listings), 10)}): ").strip()
                
                if choice == "0":
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= min(len(listings), 10):
                    selected = listings[choice_num - 1]
                    print(f"{EMOJIS['success']} Выбрано: {selected['demandStayListing']['description']['name']['localizedStringWithTranslationPreference']}")
                    return selected
                else:
                    print(f"{EMOJIS['error']} Введите число от 0 до {min(len(listings), 10)}")
                    
            except ValueError:
                print(f"{EMOJIS['error']} Введите корректное число")
    
    def get_full_listing_data(self, listing: Dict, airbnb_client, search_location) -> Dict[str, Any]:
        """
        Получение полных данных о жилье
        
        Args:
            listing: Базовая информация о жилье
            airbnb_client: Клиент для работы с MCP сервером
            search_location: Город поиска для TripAdvisor
            
        Returns:
            Dict: Полная информация о жилье с сохраненным городом
        """
        print(f"{EMOJIS['details']} Получаю детальную информацию...")
        
        # Извлекаем город из search_location
        search_city = self._extract_city_from_location(search_location)
        
        # Базовая информация из поиска
        basic_info = {
            "id": listing["id"],
            "name": listing["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"],
            "url": listing["url"],
            "rating": listing.get("avgRatingA11yLabel", "Нет рейтинга"),
            "badges": listing.get("badges", ""),
            "price_info": listing["structuredDisplayPrice"]["explanationData"]["priceDetails"],
            "coordinates": listing["demandStayListing"]["location"]["coordinate"],
            "search_city": search_city
        }
        
        # Детальная информация от MCP сервера
        details = airbnb_client.get_listing_details(listing["id"])
        
        return {
            "basic": basic_info,
            "details": details
        }
        
    def _extract_city_from_location(self, search_location: str) -> str:
        """
        Извлекает название города из location строки
        
        Args:
            search_location: "Kiev, Ukraine" или "New York, NY, USA"
            
        Returns:
            str: Название города
        """
        # Берем первую часть до запятой
        city = search_location.split(',')[0].strip()
        return city if city else "Kiev"
    
    def generate_ai_report(self, listing_data: Dict, user_request: str = "") -> str:
        """Генерация детального отчета с помощью ИИ"""
        print(f"{EMOJIS['ai']} ИИ анализирует жилье и создает отчет...")
        
        # Предобработка данных
        processed_data = self._preprocess_listing_data(listing_data)
        
        system_prompt = """Ты эксперт по недвижимости и туризму. Создай детальный отчет о жилье на Airbnb.

    Структура отчета:
    1. 🏠 ОБЩАЯ ИНФОРМАЦИЯ
    2. ⭐ РЕЙТИНГ И ОТЗЫВЫ  
    3. 💰 СТОИМОСТЬ И ЦЕННОСТЬ
    4. 🏢 РАСПОЛОЖЕНИЕ
    5. 🛏️ УДОБСТВА И ОСОБЕННОСТИ
    6. ✅ ПЛЮСЫ
    7. ⚠️ ВОЗМОЖНЫЕ МИНУСЫ (УЧИТЫВАЯ ЗАПРОС ПОЛЬЗОВАТЕЛЯ)
    8. 🎯 ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ

    Пиши живым, понятным языком. Будь честным - указывай как плюсы, так и возможные недостатки."""

        user_prompt = f"""Проанализируй это жилье:

    ОСНОВНАЯ ИНФОРМАЦИЯ:
    • Название: {processed_data['name']}
    • Рейтинг: {processed_data['rating']} 
    • Цена: {processed_data['price_per_night']}/ночь
    • Район: {processed_data['location']}
    • Особенности: {processed_data['highlights']}

    УДОБСТВА:
    {processed_data['amenities_formatted']}

    ПОЛИТИКИ:
    {processed_data['policies']}

    ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_request}

    Создай подробный отчет с учетом запроса пользователя."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"{EMOJIS['error']} Ошибка генерации отчета: {e}"

    def _preprocess_listing_data(self, listing_data: Dict) -> Dict:
        """Предобработка данных для более чистого промпта"""
        basic = listing_data["basic"]
        details = listing_data["details"]
        
        # Извлекаем ключевую информацию
        processed = {
            "name": basic["name"],
            "rating": basic["rating"],
            "price_per_night": self._extract_price_per_night(basic["price_info"]),
            "location": self._get_location_info(details),
            "highlights": self._get_highlights(details),
            "amenities_formatted": self._format_amenities(details),
            "policies": self._get_policies(details)
        }
        
        return processed

    def _extract_price_per_night(self, price_info: str) -> str:
        """Извлекает цену за ночь"""
        import re
        match = re.search(r'\$(\d+)', price_info)
        return f"${match.group(1)}" if match else "Цена не указана"

    def _get_location_info(self, details) -> str:
        """Получает информацию о локации"""
        # Если details - словарь (реальные данные)
        if isinstance(details, dict):
            details_list = details.get("details", [])
        else:
            # Если details - список (фейковые данные)
            details_list = details
        
        for detail in details_list:
            if detail.get("id") == "LOCATION_DEFAULT":
                return detail.get("subtitle", "")
        return ""

    def _get_highlights(self, details) -> str:
        """Получает основные особенности"""
        if isinstance(details, dict):
            details_list = details.get("details", [])
        else:
            details_list = details
        
        for detail in details_list:
            if detail.get("id") == "HIGHLIGHTS_DEFAULT":
                return detail.get("highlights", "")
        return ""

    def _format_amenities(self, details) -> str:
        """Форматирует удобства в читаемый список"""
        if isinstance(details, dict):
            details_list = details.get("details", [])
        else:
            details_list = details
        
        for detail in details_list:
            if detail.get("id") == "AMENITIES_DEFAULT":
                amenities_str = detail.get("seeAllAmenitiesGroups", "")
                # Остальная логика без изменений
                categories = amenities_str.split(", ")
                formatted = []
                
                for item in categories:
                    if ":" in item:
                        current_category, first_amenity = item.split(":", 1)
                        formatted.append(f"\n{current_category.strip()}:")
                        if first_amenity.strip():
                            formatted.append(f"  • {first_amenity.strip()}")
                    else:
                        formatted.append(f"  • {item.strip()}")
                
                return "".join(formatted)
        return ""

    def _get_policies(self, details) -> str:
        """Получает политики заселения"""
        if isinstance(details, dict):
            details_list = details.get("details", [])
        else:
            details_list = details
        
        for detail in details_list:
            if detail.get("id") == "POLICIES_DEFAULT":
                return detail.get("houseRulesSections", "")
        return ""
    
    def analyze_listing_full_cycle(self, listings: List[Dict], airbnb_client, 
                             user_request: str = "", search_location: str = "Kiev, Ukraine") -> str:
        """
        Полный цикл анализа: выбор → получение данных → ИИ отчет → дополнительные опции
        
        Args:
            listings: Список жилья для выбора
            airbnb_client: Клиент MCP сервера
            user_request: Оригинальный запрос пользователя
            search_location: Город поиска из ИИ анализа
            
        Returns:
            str: Результат действия пользователя ('back', 'new_search', 'exit')
        """
        # Шаг 1: Выбор жилья пользователем
        selected_listing = self.select_listing_interactive(listings)
        if not selected_listing:
            return 'back'
        
        # Шаг 2: Получение полных данных (передаем search_location)
        full_data = self.get_full_listing_data(selected_listing, airbnb_client, search_location)
        
        # Шаг 3: ИИ анализ и отчет
        report = self.generate_ai_report(full_data, user_request)
        
        # Шаг 4: Отображение результата
        self._display_ai_report(report)
        
        # Шаг 5: Предложение дополнительных опций
        return self._handle_post_analysis_options(full_data, listings, airbnb_client, user_request)
    
    def _handle_post_analysis_options(self, listing_data: Dict, listings: List[Dict], 
                                    airbnb_client, user_request: str) -> str:
        """
        Обработка опций после показа анализа жилья
        
        Args:
            listing_data: Данные проанализированного жилья
            listings: Полный список жилья для возврата к выбору
            airbnb_client: Клиент Airbnb
            user_request: Оригинальный запрос
            
        Returns:
            str: Действие пользователя
        """
                
        print(f"\n{EMOJIS['question']} Что дальше?")
        print("1. Дополнительная информация о местности (TripAdvisor)")
        print("2. Посмотреть детали другого варианта")
        print("3. Вернуться к поиску")
        print("0. Завершить")
        
        while True:
            choice = input(f"\n{EMOJIS['select']} Ваш выбор (0-3): ").strip()
            
            if choice == "0":
                return 'exit'
            elif choice == "1":
                # Запуск TripAdvisor интеграции
                return self._handle_tripadvisor_integration(listing_data, listings, airbnb_client, user_request)
            elif choice == "2":
                # Возврат к выбору другого жилья
                return self.analyze_listing_full_cycle(listings, airbnb_client, user_request)
            elif choice == "3":
                return 'new_search'
            else:
                print(f"{EMOJIS['error']} Введите число от 0 до 3")
    
    def _handle_tripadvisor_integration(self, listing_data: Dict, listings: List[Dict], 
                                      airbnb_client, user_request: str) -> str:
        """
        Обработка интеграции с TripAdvisor
        
        Args:
            listing_data: Данные о жилье
            listings: Список всего жилья
            airbnb_client: Клиент Airbnb
            user_request: Оригинальный запрос
            
        Returns:
            str: Результат действия
        """
        from tripadvisor import Integrator
    
        integrator = Integrator()
        
        try:
            # Запуск TripAdvisor сервиса
            if not integrator.start_tripadvisor_service():
                print(f"{EMOJIS['error']} Не удалось запустить TripAdvisor сервис")
                return self._handle_post_analysis_options(listing_data, listings, airbnb_client, user_request)
            
            # Цикл работы с TripAdvisor
            while True:
                choice = integrator.show_additional_options_menu(listing_data)
                
                if choice == "0":  # Завершить
                    return 'exit'
                elif choice == "5":  # Выбрать другое жилье
                    return self.analyze_listing_full_cycle(listings, airbnb_client, user_request, listing_data["basic"]["search_city"])
                elif choice == "6":  # Новый поиск
                    return 'new_search'
                else:
                    # Получение дополнительной информации
                    analysis = integrator.process_additional_info_request(choice, listing_data)
                    
                    if analysis:
                        print("\n" + "="*80)
                        print(f"{EMOJIS['tripadvisor']} АНАЛИЗ ДАННЫХ TRIPADVISOR")
                        print("="*80)
                        print(analysis)
                        print("="*80)
                        
                        input(f"\n{EMOJIS['question']} Нажмите Enter для продолжения...")
                    else:
                        print(f"{EMOJIS['error']} Не удалось получить информацию")
        
        finally:
            integrator.stop_tripadvisor_service()
    
    def _display_ai_report(self, report: str) -> None:
        """
        Красивое отображение ИИ отчета
        
        Args:
            report: Текст отчета от ИИ
        """
        print("\n" + "="*80)
        print(f"{EMOJIS['ai']} ДЕТАЛЬНЫЙ ИИ АНАЛИЗ ЖИЛЬЯ")
        print("="*80)
        print(report)
        print("="*80)