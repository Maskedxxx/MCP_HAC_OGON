# airbnb/formatter.py
"""
Модуль для форматирования и отображения результатов поиска
"""

from typing import List, Dict
from .config import DISPLAY_CONFIG, MESSAGES
from config import EMOJIS


class Formatter:
    """Класс для форматирования вывода результатов Airbnb"""
    
    def __init__(self, config: Dict = None):
        """
        Инициализация форматтера
        
        Args:
            config: Настройки отображения (опционально)
        """
        self.config = config or DISPLAY_CONFIG
    
    def format_price(self, price_text: str) -> str:
        """
        Форматирование цены из текста Airbnb
        
        Args:
            price_text: Текст с ценой от Airbnb
            
        Returns:
            str: Отформатированная цена
        """
        # Если есть информация о количестве ночей: "$87 x 5 nights: $433, "
        if "x" in price_text and "nights:" in price_text:
            try:
                # Разделяем по двоеточию: ["$87 x 5 nights", " $433, "]
                parts = price_text.split(":")
                left_part = parts[0]  # "$87 x 5 nights"
                right_part = parts[1].strip()  # "$433, "
                
                # Извлекаем цену за ночь
                price_per_night = left_part.split("x")[0].strip().replace("$", "")
                
                # Извлекаем количество ночей
                nights = left_part.split("x")[1].strip().split()[0]
                
                # Извлекаем общую цену
                total_price = right_part.replace("$", "").replace(",", "").strip()
                
                return f"${price_per_night}/ночь (${total_price} за {nights} ночей)"
            except:
                # Если парсинг не удался, возвращаем как есть
                return price_text
        
        # Если просто цена с множителем без указания общей суммы
        elif "x" in price_text:
            price_per_night = price_text.split("x")[0].strip().replace("$", "")
            return f"${price_per_night}/ночь"
        
        return price_text
    
    def extract_rating(self, rating_text: str) -> str:
        """
        Извлечение рейтинга из текста
        
        Args:
            rating_text: Текст с рейтингом
            
        Returns:
            str: Чистый рейтинг
        """
        if "out of 5" in rating_text:
            return rating_text.split(" ")[0]
        return "New"
    
    def display_search_results(self, listings: List[Dict]):
        """
        Отображение результатов поиска
        
        Args:
            listings: Список найденного жилья
        """
        if not listings:
            print(f"{EMOJIS['error']} {MESSAGES['no_results']}")
            return
        
        max_results = self.config["max_results_to_show"]
        count = len(listings)
        
        print(f"\n{EMOJIS['house']} {MESSAGES['found_results'].format(count=count)}")
        print("=" * 80)
        
        for i, listing in enumerate(listings[:max_results], 1):
            self._format_single_listing(i, listing)
    
    def _format_single_listing(self, index: int, listing: Dict):
        """
        Форматирование одного варианта жилья
        
        Args:
            index: Номер в списке
            listing: Данные о жилье
        """
        name = listing["demandStayListing"]["description"]["name"]["localizedStringWithTranslationPreference"]
        
        # Собираем информацию для отображения
        info_parts = []
        
        # Рейтинг
        if self.config["show_rating"]:
            rating_text = listing.get("avgRatingA11yLabel", "Нет рейтинга")
            rating = self.extract_rating(rating_text)
            info_parts.append(f"{EMOJIS['star']} {rating}/5")
        
        # Цена
        if self.config["show_price"]:
            price_details = listing["structuredDisplayPrice"]["explanationData"]["priceDetails"]
            formatted_price = self.format_price(price_details)
            info_parts.append(f"{EMOJIS['money']} {formatted_price}")
        
        # Значки
        if self.config["show_badges"]:
            badges = listing.get("badges", "")
            if badges:
                info_parts.append(f"{EMOJIS['trophy']} {badges}")
        
        # Вывод
        print(f"{index:2d}. {name}")
        if info_parts:
            print(f"    {' | '.join(info_parts)}")
        
        if self.config["show_url"]:
            print(f"    {EMOJIS['link']} {listing['url']}")
        
        print("-" * 80)
    
    def display_listing_details(self, details: Dict):
        """
        Отображение детальной информации о листинге
        
        Args:
            details: Детальная информация о листинге
        """
        if not details:
            return
        
        print(f"{EMOJIS['link']} URL: {details.get('listingUrl', 'N/A')}")
        
        # Обработка деталей
        for detail in details.get("details", []):
            if detail["id"] == "AMENITIES_DEFAULT":
                self._display_amenities(detail)
            elif detail["id"] == "HIGHLIGHTS_DEFAULT":
                self._display_highlights(detail)
    
    def _display_amenities(self, detail: Dict):
        """Отображение удобств"""
        amenities = detail.get("seeAllAmenitiesGroups", "")
        if not amenities:
            return
            
        print(f"\n{EMOJIS['house']} Удобства:")
        amenities_list = amenities.split(", ")
        max_amenities = self.config["max_amenities_to_show"]
        
        for amenity in amenities_list[:max_amenities]:
            print(f"   • {amenity}")
        
        if len(amenities_list) > max_amenities:
            remaining = len(amenities_list) - max_amenities
            print(f"   ... и еще {remaining} удобств")
    
    def _display_highlights(self, detail: Dict):
        """Отображение особенностей"""
        highlights = detail.get("highlights", "")
        if highlights:
            print(f"\n✨ Особенности: {highlights}")