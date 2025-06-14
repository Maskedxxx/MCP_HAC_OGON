# listing_analyzer.py
"""
Модуль для детального анализа жилья с помощью ИИ
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import OPENAI_CONFIG, EMOJIS, MESSAGES


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
    
    def get_full_listing_data(self, listing: Dict, airbnb_client) -> Dict[str, Any]:
        """
        Получение полных данных о жилье
        
        Args:
            listing: Базовая информация о жилье
            airbnb_client: Клиент для работы с MCP сервером
            
        Returns:
            Dict: Полная информация о жилье
        """
        print(f"{EMOJIS['details']} Получаю детальную информацию...")
        
        # Базовая информация из поиска
        basic_info = {
            "id": listing["id"],
            "name": listing["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"],
            "url": listing["url"],
            "rating": listing.get("avgRatingA11yLabel", "Нет рейтинга"),
            "badges": listing.get("badges", ""),
            "price_info": listing["structuredDisplayPrice"]["explanationData"]["priceDetails"],
            "coordinates": listing["demandStayListing"]["location"]["coordinate"]
        }
        
        # Детальная информация от MCP сервера
        details = airbnb_client.get_listing_details(listing["id"])
        
        return {
            "basic": basic_info,
            "details": details
        }
    
    def generate_ai_report(self, listing_data: Dict, user_request: str = "") -> str:
        """
        Генерация детального отчета с помощью ИИ
        
        Args:
            listing_data: Полная информация о жилье
            user_request: Оригинальный запрос пользователя для персонализации
            
        Returns:
            str: Детальный отчет на русском языке
        """
        print(f"{EMOJIS['ai']} ИИ анализирует жилье и создает отчет...")
        
        system_prompt = """Ты эксперт по недвижимости и туризму. Создай детальный отчет о жилье на Airbnb.

Структура отчета:
1. 🏠 ОБЩАЯ ИНФОРМАЦИЯ
2. ⭐ РЕЙТИНГ И ОТЗЫВЫ  
3. 💰 СТОИМОСТЬ И ЦЕННОСТЬ
4. 🏢 РАСПОЛОЖЕНИЕ
5. 🛏️ УДОБСТВА И ОСОБЕННОСТИ
6. ✅ ПЛЮСЫ
7. ⚠️ ВОЗМОЖНЫЕ МИНУСЫ
8. 🎯 ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ

Пиши живым, понятным языком. Будь честным - указывай как плюсы, так и возможные недостатки. 
В рекомендациях учитывай запрос пользователя."""

        user_prompt = f"""Проанализируй это жилье и создай детальный отчет:

ДАННЫЕ О ЖИЛЬЕ:
{json.dumps(listing_data, indent=2, ensure_ascii=False)}

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_request if user_request else "Общий анализ"}

Создай подробный, честный отчет с рекомендациями."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=15000,
                temperature=0.3  # Немного креативности, но в основном факты
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"{EMOJIS['error']} Ошибка генерации отчета: {e}"
    
    def analyze_listing_full_cycle(self, listings: List[Dict], airbnb_client, user_request: str = "") -> None:
        """
        Полный цикл анализа: выбор → получение данных → ИИ отчет
        
        Args:
            listings: Список жилья для выбора
            airbnb_client: Клиент MCP сервера
            user_request: Оригинальный запрос пользователя
        """
        # Шаг 1: Выбор жилья пользователем
        selected_listing = self.select_listing_interactive(listings)
        if not selected_listing:
            return
        
        # Шаг 2: Получение полных данных
        full_data = self.get_full_listing_data(selected_listing, airbnb_client)
        
        # Шаг 3: ИИ анализ и отчет
        report = self.generate_ai_report(full_data, user_request)
        
        # Шаг 4: Отображение результата
        self._display_ai_report(report)
    
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
        
        # Предложение дальнейших действий
        print(f"\n{EMOJIS['question']} Что дальше?")
        print("1. Посмотреть детали другого варианта")
        print("2. Вернуться к поиску")
        print("3. Завершить")