# tripadvisor/integrator.py
"""
Интеграция TripAdvisor MCP с анализом жилья
"""

from typing import Dict, List, Optional
from openai import OpenAI
from .client import MCPClient
from config import OPENAI_CONFIG, EMOJIS, MESSAGES


class Integrator:
    """Интегратор TripAdvisor для дополнительной информации о жилье"""
    
    def __init__(self, api_key: str = None):
        """
        Инициализация интегратора
        
        Args:
            api_key: API ключ OpenAI для ИИ анализа
        """
        self.openai_client = OpenAI(api_key=api_key or OPENAI_CONFIG["api_key"])
        self.tripadvisor_client = MCPClient()
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
            return self._get_city_search_analysis(listing_data)
        elif choice == "4":
            return self._get_area_reviews_analysis(lat, lon, location_name)
        else:
            return None
    
    def _get_enriched_places(self, places: List[Dict], place_type: str) -> List[Dict]:
        """
        Получение обогащенных данных с деталями для мест
        
        Args:
            places: Список мест от TripAdvisor
            place_type: Тип места для логирования
            
        Returns:
            List[Dict]: Обогащенные места с описаниями
        """
        print(f"{EMOJIS['details']} Получаем детали {place_type} и фильтруем...")
        enriched_places = []
        
        for i, place in enumerate(places, 1):
            location_id = place.get('location_id')
            name = place.get('name', 'N/A')
            
            print(f"  {i}. Получаю детали для: {name[:30]}...")
            
            if location_id:
                try:
                    details = self.tripadvisor_client.get_location_details(location_id)
                    description = details.get('description', '')
                    features = details.get('features', [])
                    
                    desc_len = len(description)
                    features_count = len(features)
                    
                    if desc_len > 0:
                        enriched_place = {
                            **place,
                            'description': description,
                            'features': features
                        }
                        enriched_places.append(enriched_place)
                        print(f"     ✅ Описание: {desc_len} символов, Особенности: {features_count}")
                        
                        if len(enriched_places) >= 5:
                            break
                    else:
                        print("     ⏭️ Пропускаю - нет описания")
                        
                except Exception as e:
                    print(f"     ❌ Ошибка получения деталей: {e}")
            else:
                print("     ⏭️ Пропускаю - нет location_id")
        
        print(f"   📊 Найдено {place_type} с описанием: {len(enriched_places)}")
        return enriched_places
    
    def _get_restaurants_analysis(self, lat: float, lon: float, location_name: str) -> str:
        """Анализ ресторанов рядом"""
        print(f"{EMOJIS['restaurant']} Ищу рестораны рядом с жильем...")
        
        restaurants = self.tripadvisor_client.search_nearby_locations(lat, lon, "restaurants")
        
        if not restaurants:
            return f"{EMOJIS['error']} Рестораны рядом не найдены"
        
        enriched_restaurants = self._get_enriched_places(restaurants, "ресторанов")
        
        if not enriched_restaurants:
            return f"{EMOJIS['error']} Рестораны с описанием не найдены"
        
        return self._generate_tripadvisor_analysis(
            enriched_restaurants, 
            "ресторанов", 
            f"рядом с жильем {location_name}"
        )
    
    def _get_attractions_analysis(self, lat: float, lon: float, location_name: str) -> str:
        """Анализ достопримечательностей рядом"""
        print(f"{EMOJIS['attraction']} Ищу достопримечательности рядом...")
        
        attractions = self.tripadvisor_client.search_nearby_locations(lat, lon, "attractions")
        
        if not attractions:
            return f"{EMOJIS['error']} Достопримечательности рядом не найдены"
        
        enriched_attractions = self._get_enriched_places(attractions, "достопримечательностей")
        
        if not enriched_attractions:
            return f"{EMOJIS['error']} Достопримечательности с описанием не найдены"
        
        return self._generate_tripadvisor_analysis(
            enriched_attractions, 
            "достопримечательностей", 
            f"рядом с жильем {location_name}"
        )
    
    def _get_city_search_analysis(self, listing_data: Dict) -> str:
        """Анализ города по сохраненному названию"""
        city = listing_data["basic"]["search_city"]
        print(f"{EMOJIS['search']} Ищу информацию о городе {city}...")
        
        city_info = self.tripadvisor_client.search_locations(f"{city} attractions")
        
        if not city_info:
            return f"{EMOJIS['error']} Информация о городе {city} не найдена"
        
        enriched_city_info = self._get_enriched_places(city_info, "мест в городе")
        
        if not enriched_city_info:
            return f"{EMOJIS['error']} Места в городе с описанием не найдены"
        
        return self._generate_tripadvisor_analysis(
            enriched_city_info, 
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
    
    def _generate_tripadvisor_analysis(self, data: List[Dict], data_type: str, context: str) -> str:
        """
        Генерация ИИ анализа для данных TripAdvisor
        
        Args:
            data: Данные от TripAdvisor
            data_type: Тип данных (рестораны, достопримечательности и т.д.)
            context: Контекст (где находятся)
            
        Returns:
            str: ИИ анализ
        """
        print(f"{EMOJIS['ai']} Создаю анализ {data_type}...")
        
        system_prompt = f"""Ты эксперт по туризму. Создай краткий обзор {data_type} {context}.
        
Структура:
1. 📍 ОБЩАЯ ИНФОРМАЦИЯ
2. ⭐ ТОП-3 МЕСТА
3. 💡 РЕКОМЕНДАЦИИ

Будь кратким и информативным."""

        user_prompt = f"""Проанализируй эти {data_type} {context}:

{self._format_tripadvisor_data(data)}

Создай краткий обзор на русском языке."""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"{EMOJIS['error']} Ошибка генерации анализа: {e}"
    
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
        """Форматирование обогащенных данных TripAdvisor для ИИ"""
        formatted = []
        for i, item in enumerate(data, 1):
            name = item.get("name", "N/A")
            address = item.get("address_obj", {}).get("address_string", "N/A")
            
            # Новые поля с деталями
            description = item.get("description", "")
            features = item.get("features", [])
            
            # Базовая информация
            entry = f"{i}. {name}\n   Адрес: {address}"
            
            # Добавляем описание если есть
            if description:
                # Обрезаем длинные описания
                desc_short = description[:200] + "..." if len(description) > 200 else description
                entry += f"\n   Описание: {desc_short}"
            
            # Добавляем особенности если есть
            if features:
                features_str = ", ".join(features[:5])  # Максимум 5 особенностей
                entry += f"\n   Особенности: {features_str}"
                if len(features) > 5:
                    entry += f" (еще {len(features) - 5})"
            
            formatted.append(entry)
        
        return "\n\n".join(formatted)