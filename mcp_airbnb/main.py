# main.py
"""
Главный файл приложения для поиска жилья на Airbnb
"""

from airbnb_client import AirbnbMCPClient
from formatter import AirbnbFormatter
from config import EMOJIS


def main():
    """Основная функция приложения"""
    client = AirbnbMCPClient()
    formatter = AirbnbFormatter()
    
    try:
        # Запускаем сервер
        if not client.start_server():
            return
        
        # Демонстрация поиска
        print("\n" + "="*60)
        print("🎯 ДЕМОНСТРАЦИЯ AIRBNB MCP КЛИЕНТА")
        print("="*60)
        
        # Поиск жилья - легко настраивается через параметры
        listings = client.search_accommodations(
            location="Kiev, Ukraine",
            adults=2,
            checkin="2025-07-01",  # Можно добавить даты
            checkout="2025-07-05"
        )
        
        # Отображение результатов
        formatter.display_search_results(listings)
        
        # Детали первого варианта
        if listings:
            print("\n📋 ДЕТАЛИ ПЕРВОГО ВАРИАНТА:")
            print("="*50)
            
            first_listing_id = listings[0]["id"]
            details = client.get_listing_details(first_listing_id)
            formatter.display_listing_details(details)
        
        print(f"\n{EMOJIS['finish']} Тест завершен успешно!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Программа остановлена пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        client.stop_server()


def search_custom_location(location: str, adults: int = 2, **kwargs):
    """
    Функция для поиска в определенном месте с настройками
    
    Args:
        location: Город для поиска
        adults: Количество взрослых
        **kwargs: Дополнительные параметры
    """
    client = AirbnbMCPClient()
    formatter = AirbnbFormatter()
    
    try:
        if client.start_server():
            listings = client.search_accommodations(location, adults=adults, **kwargs)
            formatter.display_search_results(listings)
            return listings
    finally:
        client.stop_server()
    
    return []


if __name__ == "__main__":
    main()