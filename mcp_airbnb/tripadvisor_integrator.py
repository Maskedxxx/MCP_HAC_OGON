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
        
        Args:
            choice: Выбор пользователя
            listing_data: Данные о жилье
            
        Returns:
            Optional[str]: ИИ отчет или None для возврата/завершения
        """
        coordinates = listing_data["basic"]["coordinates"]
        lat, lon = coordinates["latitude"], coordinates["longitude"]
        
        # Извлекаем город из адреса или названия
        location_name = listing_data["basic"]["name"]
        
        if choice == "1":
            return self._get_restaurants_analysis(lat, lon, location_name)
        elif choice == "2":
            return self._get_attractions_analysis(lat, lon, location_name)
        elif choice == "3":
            return self._get_city_search_analysis(location_name)
        elif choice == "4":
            return self._get_area_reviews_analysis(lat, lon, location_name)
        else:
            return None  # Возврат/завершение
    
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
    
    def _get_city_search_analysis(self, location_name: str) -> str:
        """Анализ города по поиску"""
        # Извлекаем название города из локации
        city = self._extract_city_name(location_name)
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
        """Анализ отзывов о районе"""
        print(f"{EMOJIS['review']} Ищу отзывы о районе...")
        
        # Ищем места рядом и берем отзывы первого
        nearby_places = self.tripadvisor_client.search_nearby_locations(lat, lon)
        
        if not nearby_places:
            return f"{EMOJIS['error']} Места для анализа отзывов не найдены"
        
        # Берем первое место и получаем его отзывы
        first_place = nearby_places[0]
        location_id = first_place.get("location_id")
        
        if not location_id:
            return f"{EMOJIS['error']} Не удалось получить ID локации для отзывов"
        
        reviews = self.tripadvisor_client.get_location_reviews(location_id)
        
        if not reviews:
            return f"{EMOJIS['error']} Отзывы о районе не найдены"
        
        return self._generate_reviews_analysis(reviews[:3], first_place["name"], location_name)
    
    def _generate_tripadvisor_analysis(self, data: List[Dict], data_type: str, context: str) -> str:
        """
        Генерация ИИ анализа данных TripAdvisor
        
        Args:
            data: Данные от TripAdvisor
            data_type: Тип данных (ресторанов, достопримечательностей и т.д.)
            context: Контекст (название жилья/города)
            
        Returns:
            str: ИИ анализ
        """
        print(f"{EMOJIS['ai']} {MESSAGES['tripadvisor_analysis']}...")
        
        system_prompt = f"""Ты эксперт по туризму. Проанализируй данные о {data_type} от TripAdvisor и создай краткий полезный отчет.

Структура отчета:
1. 🎯 КРАТКАЯ СВОДКА
2. 📍 ТОП РЕКОМЕНДАЦИИ (3-5 лучших мест)
3. 💡 ПОЛЕЗНЫЕ СОВЕТЫ

Пиши живым языком, будь конкретным и полезным."""

        user_prompt = f"""Проанализируй {data_type} {context}:

ДАННЫЕ TRIPADVISOR:
{self._format_tripadvisor_data(data)}

Создай краткий практичный отчет для туриста."""

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
            return f"{EMOJIS['error']} Ошибка анализа TripAdvisor: {e}"
    
    def _generate_reviews_analysis(self, reviews: List[Dict], place_name: str, context: str) -> str:
        """Генерация анализа отзывов"""
        print(f"{EMOJIS['ai']} Анализирую отзывы о районе...")
        
        system_prompt = """Ты эксперт по анализу отзывов туристов. Проанализируй отзывы и создай краткий отчет о районе.

Структура:
1. 🏘️ ОБЩЕЕ ВПЕЧАТЛЕНИЕ О РАЙОНЕ
2. ✅ ЧТО ХВАЛЯТ ТУРИСТЫ
3. ⚠️ НА ЧТО ЖАЛУЮТСЯ
4. 💡 РЕКОМЕНДАЦИИ ДЛЯ ГОСТЕЙ

Будь объективным, выделяй ключевые моменты."""

        user_prompt = f"""Отзывы о месте "{place_name}" в районе жилья {context}:

ОТЗЫВЫ:
{self._format_reviews_data(reviews)}

Создай анализ района на основе этих отзывов."""

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
            return f"{EMOJIS['error']} Ошибка анализа отзывов: {e}"
    
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
    
    def _extract_city_name(self, location_name: str) -> str:
        """Извлечение названия города из названия жилья"""
        # Простое извлечение - можно улучшить
        common_words = ["apartment", "studio", "room", "house", "flat", "place", "home"]
        words = location_name.lower().split()
        
        for word in words:
            if word not in common_words and len(word) > 3:
                return word.capitalize()
        
        return "Kiev"  # По умолчанию