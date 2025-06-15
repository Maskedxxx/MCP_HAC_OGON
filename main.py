# main.py
"""
Главный файл приложения для поиска жилья на Airbnb с ИИ агентом
"""

from airbnb import MCPClient as AirbnbClient, Formatter
from shared import AIAgent, ListingAnalyzer
from config import EMOJIS, MESSAGES


def interactive_search():
    """Интерактивный режим с вводом пользователя"""
    # Инициализация компонентов
    airbnb_client = AirbnbClient()
    formatter = Formatter()
    ai_agent = AIAgent()
    analyzer = ListingAnalyzer()
    
    try:
        # Запуск Airbnb сервера
        if not airbnb_client.start_server():
            return
        
        # Заголовок
        print("\n" + "="*60)
        print(MESSAGES['interactive_title'])
        print("="*60)
        print(MESSAGES['interactive_help'])
        print(MESSAGES['interactive_examples'])
        print(MESSAGES['interactive_exit'])
        
        # Основной цикл
        while True:
            print(f"\n{EMOJIS['user']} ", end="")
            user_request = input("Ваш запрос: ").strip()
            
            if user_request.lower() in ['выход', 'quit', 'exit', '']:
                break
            
            print("-" * 60)
            
            # ИИ анализ и поиск
            listings, search_location = ai_agent.search_with_ai(
                user_request, 
                airbnb_client, 
                formatter
            )
            
            if listings:
                # Предлагаем детальный анализ
                print(f"\n{EMOJIS['question']} {MESSAGES['interactive_analyze_prompt']}", end="")
                choice = input().strip().lower()
                
                if choice in ['y', 'yes', 'да', 'д']:
                    result = analyzer.analyze_listing_full_cycle(
                        listings, 
                        airbnb_client, 
                        user_request, 
                        search_location
                    )
                    
                    if result == 'exit':
                        break
                    elif result == 'new_search':
                        continue  # Продолжаем цикл для нового поиска
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Программа остановлена пользователем")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка: {e}")
    finally:
        airbnb_client.stop_server()
        print(f"\n{EMOJIS['finish']} До свидания!")


def main():
    """Главная функция приложения"""
    print("🏠 ДОБРО ПОЖАЛОВАТЬ В AIRBNB ПОИСК С ИИ!")
    interactive_search()


if __name__ == "__main__":
    main()