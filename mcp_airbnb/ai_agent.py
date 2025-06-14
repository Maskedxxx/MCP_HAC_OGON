# ai_agent.py
"""
ИИ агент для преобразования человеческих запросов в параметры поиска
"""

import json
from typing import Dict, Any
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
from config import OPENAI_CONFIG, MESSAGES, EMOJIS


class AirbnbSearchParams(BaseModel):
    """Параметры для поиска Airbnb"""
    location: str
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    adults: Optional[int] = None
    children: Optional[int] = None
    infants: Optional[int] = None
    pets: Optional[int] = None
    minPrice: Optional[int] = None
    maxPrice: Optional[int] = None


class AirbnbAIAgent:
    """ИИ агент для работы с запросами пользователей"""
    
    def __init__(self, api_key: str = None):
        """
        Инициализация агента
        
        Args:
            api_key: API ключ OpenAI (если не указан, берется из config)
        """
        self.api_key = api_key or OPENAI_CONFIG["api_key"]
        self.client = OpenAI(api_key=self.api_key)
        self.model = OPENAI_CONFIG["model"]
    
    def get_search_function_description(self, airbnb_client) -> Dict[str, Any]:
        """
        Получает описание функции поиска от MCP сервера
        
        Args:
            airbnb_client: Экземпляр AirbnbMCPClient
            
        Returns:
            Dict: Описание функции поиска
        """
        print(f"{EMOJIS['search']} {MESSAGES['getting_function_description']}")
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_response = airbnb_client.send_request("tools/list", {})
        
        # Ищем airbnb_search среди доступных инструментов
        for tool in tools_response.get("result", {}).get("tools", []):
            if tool["name"] == "airbnb_search":
                return tool
        
        raise ValueError("Функция airbnb_search не найдена в MCP сервере")
    
    def parse_user_request(self, user_request: str, tool_description: Dict) -> AirbnbSearchParams:
        """
        Преобразует запрос пользователя в параметры поиска
        
        Args:
            user_request: Запрос пользователя на естественном языке
            tool_description: Описание функции поиска от MCP сервера
            
        Returns:
            AirbnbSearchParams: Структурированные параметры поиска
        """
        print(f"{EMOJIS['ai']} {MESSAGES['parsing_request']}")
        
        system_prompt = f"""Ты эксперт по поиску жилья на Airbnb. 
        
Твоя задача - преобразовать запрос пользователя в структурированные параметры для поиска.

Описание функции поиска:
{json.dumps(tool_description, indent=2, ensure_ascii=False)}

Правила:
1. Извлекай только ту информацию, которая есть в запросе
2. Если что-то не указано - оставляй null
3. Даты форматируй как YYYY-MM-DD
4. Цены указывай в долларах без символа $
5. Количество людей - только числа

Примеры:
- "в Киев на выходные" → location: "Kiev, Ukraine", остальное null
- "в Нью-Йорк с 15 июля по 20 июля для 3 человек" → location, checkin, checkout, adults
- "дешево до 30 долларов" → maxPrice: 30"""

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_request}
                ],
                response_format=AirbnbSearchParams
            )
            
            return completion.choices[0].message.parsed
            
        except Exception as e:
            print(f"{EMOJIS['error']} {MESSAGES['ai_error'].format(error=e)}")
            # Возвращаем базовые параметры если ИИ не сработал
            return AirbnbSearchParams(location="Kiev, Ukraine")
    
    def search_with_ai(self, user_request: str, airbnb_client, formatter) -> None:
        """
        Полный цикл: получение запроса пользователя → ИИ анализ → поиск → отображение
        
        Args:
            user_request: Запрос пользователя
            airbnb_client: Клиент для работы с Airbnb
            formatter: Форматтер для вывода результатов
        """
        try:
            # Получаем описание функции поиска
            tool_description = self.get_search_function_description(airbnb_client)
            
            # ИИ анализирует запрос пользователя
            search_params = self.parse_user_request(user_request, tool_description)
            
            # Показываем что извлек ИИ
            print(f"\n{EMOJIS['robot']} {MESSAGES['ai_extracted_params']}:")
            self._display_extracted_params(search_params)
            
            # Выполняем поиск с извлеченными параметрами
            search_dict = search_params.model_dump(exclude_none=True)  # Убираем None значения
            listings = airbnb_client.search_accommodations(**search_dict)
            
            # Отображаем результаты
            formatter.display_search_results(listings)
            
            return listings
            
        except Exception as e:
            print(f"{EMOJIS['error']} {MESSAGES['search_failed'].format(error=e)}")
            return []
    
    def _display_extracted_params(self, params: AirbnbSearchParams) -> None:
        """
        Отображает извлеченные ИИ параметры
        
        Args:
            params: Параметры поиска
        """
        param_dict = params.model_dump(exclude_none=True)
        
        for key, value in param_dict.items():
            # Переводим названия параметров на русский
            russian_names = {
                "location": "Место",
                "checkin": "Заезд",
                "checkout": "Выезд", 
                "adults": "Взрослые",
                "children": "Дети",
                "infants": "Младенцы",
                "pets": "Животные",
                "minPrice": "Мин. цена",
                "maxPrice": "Макс. цена"
            }
            
            russian_name = russian_names.get(key, key)
            print(f"   • {russian_name}: {value}")