# main.py
"""
Главный файл приложения для поиска жилья на Airbnb с ИИ агентом
"""

from airbnb_client import AirbnbMCPClient
from formatter import AirbnbFormatter
from ai_agent import AirbnbAIAgent
from config import EMOJIS, MESSAGES


def demo_ai_search():
    """Демонстрация работы с ИИ агентом"""
    client = AirbnbMCPClient()
    formatter = AirbnbFormatter()
    ai_agent = AirbnbAIAgent()
    
    try:
        # Запускаем сервер
        if not client.start_server():
            return
        
        print("\n" + "="*70)
        print(f"{MESSAGES['ai_demo_start']}")
        print("="*70)
        
        # Список тестовых запросов пользователей
        test_requests = [
            "Мне нужно жилье в Киеве на неделю в июле для двоих",
            "Хочу в Нью-Йорк дешево, максимум 50 долларов за ночь, я с собакой",
            "Поездка в Париж с 15 августа по 20 августа для семьи с двумя детьми",
            "Найди что-то в Лондоне не дороже 100$ на выходные"
        ]
        
        # Обрабатываем каждый запрос
        for i, user_request in enumerate(test_requests, 1):
            print(f"\n{EMOJIS['user']} ТЕСТ {i}: {user_request}")
            print("-" * 70)
            
            # ИИ анализирует запрос и выполняет поиск
            listings = ai_agent.search_with_ai(user_request, client, formatter)
            
            if i < len(test_requests):  # Пауза между тестами кроме последнего
                input(f"\n{EMOJIS['brain']} Нажмите Enter для следующего теста...")
        
        print(f"\n{EMOJIS['finish']} Все тесты завершены!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Программа остановлена пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        client.stop_server()


def interactive_search():
    """Интерактивный режим с вводом пользователя"""
    client = AirbnbMCPClient()
    formatter = AirbnbFormatter()
    ai_agent = AirbnbAIAgent()
    
    try:
        if not client.start_server():
            return
        
        print("\n" + "="*60)
        print("🎯 ИНТЕРАКТИВНЫЙ ПОИСК ЖИЛЬЯ С ИИ")
        print("="*60)
        print("Опишите что вам нужно на обычном языке!")
        print("Примеры: 'Киев на выходные для двоих', 'Лондон дешево с собакой'")
        print("Введите 'выход' для завершения")
        
        while True:
            print(f"\n{EMOJIS['user']} ", end="")
            user_request = input("Ваш запрос: ").strip()
            
            if user_request.lower() in ['выход', 'quit', 'exit', '']:
                break
            
            print("-" * 60)
            ai_agent.search_with_ai(user_request, client, formatter)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Программа остановлена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        client.stop_server()


def old_demo():
    """Старая демонстрация с фиксированными параметрами (для сравнения)"""
    client = AirbnbMCPClient()
    formatter = AirbnbFormatter()
    
    try:
        if not client.start_server():
            return
        
        print("\n" + "="*60)
        print("📊 СТАРЫЙ СПОСОБ (фиксированные параметры)")
        print("="*60)
        
        # Поиск с фиксированными параметрами
        listings = client.search_accommodations(
            location="Kiev, Ukraine",
            adults=2,
            checkin="2025-07-01",
            checkout="2025-07-05"
        )
        
        formatter.display_search_results(listings)
        
        print(f"\n{EMOJIS['finish']} Старый тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        client.stop_server()


def main():
    """Главная функция с выбором режима"""
    print("🏠 ДОБРО ПОЖАЛОВАТЬ В AIRBNB ПОИСК С ИИ!")
    print("\nВыберите режим:")
    print("1. 🤖 Демонстрация ИИ агента (автоматические тесты)")
    print("2. 💬 Интерактивный поиск (вводите свои запросы)")
    print("3. 📊 Старый способ (для сравнения)")
    print("4. 🚪 Выход")
    
    while True:
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == "1":
            demo_ai_search()
            break
        elif choice == "2":
            interactive_search()
            break
        elif choice == "3":
            old_demo()
            break
        elif choice == "4":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Введите число от 1 до 4")


if __name__ == "__main__":
    main()