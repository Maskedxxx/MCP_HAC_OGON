# tripadvisor_integrator.py
"""
Интеграция TripAdvisor MCP с анализом жилья
"""

from typing import Dict, List, Any, Optional
from openai import OpenAI
from tripadvisor_client import TripAdvisorMCPClient
from config import OPENAI_CONFIG, EMOJIS, MESSAGES


class TripAdvisorIntegrator:
    """Интегратор TripAdvisor для дополнительной информации о жилье"""
    
    def __init__(self, api_key: str = None):
        """
        Инициализация интегратора
        
        Args:
            api_key: API ключ OpenAI для ИИ анализа
        """
        self.openai_client = OpenAI(api_key=api_key or OPENAI_CONFIG["api_key"])
        self.tripadvisor_client = TripAdvisorMCPClient()
        self.model = OPENAI_CONFIG["model"]
    
    def start_tripadvisor_service(self) -> bool:
        """
        Запуск TripAdvisor сервиса
        
        Returns:
            bool: Успешность запуска
        """
        return self.tripadvisor_client.start_server()
    
    def stop_tripadvisor_service(self):
        """Остановка TripAdvisor сервиса"""
        self.tripadvisor_client.stop_server()
    
    def show_additional_options_menu(self, listing_data: Dict) -> str:
        """
        Показать меню дополнительных опций
        
        Args:
            listing_data: Данные о жилье
            
        Returns:
            str: Выбранная опция
        """
        location_name = listing_data["basic"]["name"]
        coordinates = listing_data["basic"]["coordinates"]
        
        print(f"\n{EMOJIS['tripadvisor']} {MESSAGES['additional_info_menu'].upper()}")
        print("="*60)
        print(f"Жилье: {location_name}")
        print(f"Координаты: {coordinates['latitude']}, {coordinates['longitude']}")
        print("\nВыберите дополнительную информацию:")
        print(f"1. {EMOJIS['restaurant']} Рестораны рядом")
        print(f"2. {EMOJIS['attraction']} Достопримечательности рядом")
        print(f"3. {EMOJIS['search']} Поиск по названию города")
        print(f"4. {EMOJIS['review']} Отзывы о районе")
        print(f"5. {EMOJIS['back']} Выбрать другое жилье")
        print(f"6. {EMOJIS['house']} Новый поиск жилья")
        print("0. Завершить")
        
        while True:
            choice = input(f"\n{EMOJIS['select']} Ваш выбор (0-6): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6']:
                return choice
            print(f"{EMOJIS['error']} Введите число от 0 до 6")
    
    def process_additional_info_request(self, choice: str, listing_data: Dict) -> Optional[str]:
        """
        Обработка запроса дополнительной информации
        """
        coordinates = listing_data["basic"]["coordinates"]
        lat, lon = coordinates["latitude"], coordinates["longitude"]
        location_name = listing_data["basic"]["name"]
        
        if choice == "1":
            return self._get_restaurants_analysis(lat, lon, location_name)
        elif choice == "2":
            return self._get_attractions_analysis(lat, lon, location_name)
        elif choice == "3":
            return self._get_city_search_analysis(listing_data)  # ← Передаем весь listing_data
        elif choice == "4":
            return self._get_area_reviews_analysis(lat, lon, location_name)
        else:
            return None
    
    def _get_restaurants_analysis(self, lat: float, lon: float, location_name: str) -> str:
        """Анализ ресторанов рядом"""
        print(f"{EMOJIS['restaurant']} Ищу рестораны рядом с жильем...")
        
        restaurants = self.tripadvisor_client.search_nearby_locations(lat, lon, "restaurants")
        
        if not restaurants:
            return f"{EMOJIS['error']} Рестораны рядом не найдены"
        
        return self._generate_tripadvisor_analysis(
            restaurants[:5], 
            "ресторанов", 
            f"рядом с жильем {location_name}"
        )
    
    def _get_attractions_analysis(self, lat: float, lon: float, location_name: str) -> str:
        """Анализ достопримечательностей рядом"""
        print(f"{EMOJIS['attraction']} Ищу достопримечательности рядом...")
        
        attractions = self.tripadvisor_client.search_nearby_locations(lat, lon, "attractions")
        
        if not attractions:
            return f"{EMOJIS['error']} Достопримечательности рядом не найдены"
        
        return self._generate_tripadvisor_analysis(
            attractions[:5], 
            "достопримечательностей", 
            f"рядом с жильем {location_name}"
        )
    
    def _get_city_search_analysis(self, listing_data: Dict) -> str:
        """Анализ города по сохраненному названию"""
        # Используем сохраненный город вместо извлечения из названия жилья
        city = listing_data["basic"]["search_city"]
        print(f"{EMOJIS['search']} Ищу информацию о городе {city}...")
        
        city_info = self.tripadvisor_client.search_locations(f"{city} attractions")
        
        if not city_info:
            return f"{EMOJIS['error']} Информация о городе {city} не найдена"
        
        return self._generate_tripadvisor_analysis(
            city_info[:7], 
            "мест в городе", 
            city
        )
    
    def _get_area_reviews_analysis(self, lat: float, lon: float, location_name: str) -> str:
        """Анализ отзывов о районе с нескольких мест"""
        print(f"{EMOJIS['review']} Собираю отзывы о районе с разных мест...")
        
        # Получаем отзывы с мест где они есть
        aggregated_reviews = self._collect_reviews_from_available_places(lat, lon)
        
        if not aggregated_reviews:
            return f"{EMOJIS['error']} Отзывы о районе не найдены"
        
        return self._generate_aggregated_reviews_analysis(aggregated_reviews, location_name)
    
    def _collect_reviews_from_available_places(self, lat: float, lon: float) -> List[Dict]:
        """
        Собираем отзывы только с ресторанов и достопримечательностей
        """
        aggregated_reviews = []
        
        # Ищем ОТДЕЛЬНО достопримечательности и рестораны
        print("   🎭 Ищу достопримечательности...")
        attractions = self.tripadvisor_client.search_nearby_locations(lat, lon, "attractions")
        print(f"   ✅ Найдено достопримечательностей: {len(attractions)}")
        
        print("   🍽️ Ищу рестораны...")
        restaurants = self.tripadvisor_client.search_nearby_locations(lat, lon, "restaurants")
        print(f"   ✅ Найдено ресторанов: {len(restaurants)}")
        
        # Объединяем списки (сначала достопримечательности, потом рестораны)
        target_places = attractions[:4] + restaurants[:4]  # По 4 каждого типа максимум
        
        if not target_places:
            return []
        
        print(f"   📍 Отобрано мест для проверки: {len(target_places)}")
        
        # Собираем отзывы только с отобранных мест
        places_with_reviews = 0
        target_reviews = 12
        
        for i, place in enumerate(target_places, 1):
            name = place.get('name', 'Unknown')
            location_id = place.get('location_id')
            
            # Определяем тип места для логирования
            place_type = "🎭" if i <= len(attractions[:4]) else "🍽️"
            
            if not location_id:
                continue
            
            print(f"   {place_type} Проверяю место {i}: {name[:30]}...")
            
            try:
                reviews = self.tripadvisor_client.get_location_reviews(location_id)
                review_count = len(reviews)
                
                if review_count > 0:
                    places_with_reviews += 1
                    print(f"   ✅ Найдено отзывов: {review_count}")
                    
                    # Берем до 3 отзывов с этого места
                    reviews_to_take = min(3, review_count)
                    for review in reviews[:reviews_to_take]:
                        aggregated_reviews.append({
                            **review,
                            'source_place': name,
                            'source_type': 'attraction' if i <= len(attractions[:4]) else 'restaurant',
                            'source_location_id': location_id
                        })
                    
                    # Останавливаемся если собрали достаточно отзывов
                    if len(aggregated_reviews) >= target_reviews:
                        break
                else:
                    print("   ⚠️ Нет отзывов")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        print(f"   📊 Итог: {len(aggregated_reviews)} отзывов с {places_with_reviews} мест")
        return aggregated_reviews
    
    
        
    def _generate_aggregated_reviews_analysis(self, aggregated_reviews: List[Dict], context: str) -> str:
        """
        Генерация анализа района на основе собранных отзывов
        """
        print(f"{EMOJIS['ai']} Анализирую {len(aggregated_reviews)} отзывов о районе...")
        
        # Подготовка информации об источниках
        sources_info = self._prepare_sources_summary(aggregated_reviews)
        
        system_prompt = """Ты эксперт по анализу отзывов туристов. Проанализируй отзывы с разных мест в районе и создай объективный отчет о районе в целом.

    ВАЖНО: 
    - Фокусируйся на информации О РАЙОНЕ (транспорт, безопасность, атмосфера, удобства)
    - ИГНОРИРУЙ специфику конкретных мест (качество еды в ресторане, сервис отеля)
    - Ищи общие упоминания о районе, его характеристиках

    Структура:
    1. 🏘️ ОБЩЕЕ ВПЕЧАТЛЕНИЕ О РАЙОНЕ
    2. ✅ ЧТО ХВАЛЯТ ТУРИСТЫ
    3. ⚠️ НА ЧТО ЖАЛУЮТСЯ
    4. 💡 РЕКОМЕНДАЦИИ ДЛЯ ГОСТЕЙ

    Создай объективный анализ района на основе ВСЕХ отзывов."""

        user_prompt = f"""Анализ района жилья {context} на основе отзывов с разных мест:

    ИСТОЧНИКИ ОТЗЫВОВ:
    {sources_info}

    ОТЗЫВЫ:
    {self._format_aggregated_reviews_data(aggregated_reviews)}

    Создай анализ РАЙОНА (не конкретных мест) на основе всех отзывов."""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"{EMOJIS['error']} Ошибка анализа отзывов: {e}"

    def _prepare_sources_summary(self, aggregated_reviews: List[Dict]) -> str:
        """Подготовка сводки об источниках отзывов"""
        sources = {}
        for review in aggregated_reviews:
            place_name = review.get('source_place', 'Unknown')
            
            if place_name not in sources:
                sources[place_name] = 0
            sources[place_name] += 1
        
        summary_lines = []
        for place, count in sources.items():
            summary_lines.append(f"• {place} - {count} отзыва")
        
        return "\n".join(summary_lines)

    def _format_aggregated_reviews_data(self, aggregated_reviews: List[Dict]) -> str:
        """Форматирование отзывов для ИИ анализа"""
        formatted = []
        for i, review in enumerate(aggregated_reviews, 1):
            title = review.get("title", "Без заголовка")
            text = review.get("text", "Нет текста")
            rating = review.get("rating", "Нет рейтинга")
            source_place = review.get("source_place", "Неизвестное место")
            
            formatted.append(f"Отзыв {i} (источник: {source_place}):\n"
                            f"Заголовок: {title}\n"
                            f"Рейтинг: {rating}\n"
                            f"Текст: {text[:250]}...")
        
        return "\n\n".join(formatted)
    
    
    
    def _format_tripadvisor_data(self, data: List[Dict]) -> str:
        """Форматирование данных TripAdvisor для ИИ"""
        formatted = []
        for i, item in enumerate(data, 1):
            name = item.get("name", "N/A")
            address = item.get("address_obj", {}).get("address_string", "N/A")
            location_id = item.get("location_id", "N/A")
            
            formatted.append(f"{i}. {name}\n   Адрес: {address}\n   ID: {location_id}")
        
        return "\n\n".join(formatted)
    
    def _format_reviews_data(self, reviews: List[Dict]) -> str:
        """Форматирование отзывов для ИИ"""
        formatted = []
        for i, review in enumerate(reviews, 1):
            title = review.get("title", "Без заголовка")
            text = review.get("text", "Нет текста")
            rating = review.get("rating", "Нет рейтинга")
            
            formatted.append(f"Отзыв {i}:\nЗаголовок: {title}\nРейтинг: {rating}\nТекст: {text[:200]}...")
        
        return "\n\n".join(formatted)
    