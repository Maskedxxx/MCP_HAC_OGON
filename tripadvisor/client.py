# tripadvisor/client.py
"""
Клиент для работы с TripAdvisor MCP сервером
"""

import subprocess
import json
import os
from typing import Dict, List, Any, Optional
from .config import TRIPADVISOR_CONFIG, MESSAGES
from config import EMOJIS


class MCPClient:
    """
    Клиент для взаимодействия с TripAdvisor MCP сервером
    
    ВАЖНО: Использует обходной путь для поиска по координатам из-за бага 
    в TripAdvisor MCP сервере (search_nearby_locations не работает корректно)
    """
    
    def __init__(self, api_key: str = None):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ TripAdvisor
        """
        self.api_key = api_key or TRIPADVISOR_CONFIG["api_key"]
        self.process: Optional[subprocess.Popen] = None
        self.default_language = TRIPADVISOR_CONFIG["default_language"]
    
    def start_server(self) -> bool:
        """
        Запуск TripAdvisor MCP сервера
        
        Returns:
            bool: True если сервер успешно запущен
        """
        print(f"{EMOJIS['start']} {MESSAGES['starting_server']}")
        
        if not self.api_key or "YOUR_API_KEY" in self.api_key:
            print(f"{EMOJIS['error']} {MESSAGES['api_key_missing']}")
            return False
        
        try:
            # Передаем API ключ через переменные окружения
            env = os.environ.copy()
            env['TRIPADVISOR_API_KEY'] = self.api_key
            
            self.process = subprocess.Popen(
                TRIPADVISOR_CONFIG["mcp_command"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                env=env
            )
            
            # Ждем пока сервер запустится
            startup_line = self.process.stderr.readline()
            print(f"{EMOJIS['success']} {startup_line.strip()}")
            
            # Инициализация сервера
            self._initialize_server()
            return True
            
        except Exception as e:
            print(f"{EMOJIS['error']} {MESSAGES['server_error'].format(error=e)}")
            return False
    
    def _initialize_server(self) -> None:
        """Инициализация MCP сервера"""
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "airbnb-travel-assistant", "version": "1.0.0"}
            }
        }
        
        self.send_request("initialize", init_message["params"])
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправка запроса к TripAdvisor MCP серверу
        
        Args:
            method: Метод для вызова
            params: Параметры запроса
            
        Returns:
            Dict: Ответ от сервера
        """
        if not self.process:
            raise RuntimeError("TripAdvisor сервер не запущен")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Читаем ответ
        response_line = self.process.stdout.readline()
        return json.loads(response_line) if response_line else {}
    
    def search_locations(self, search_query: str, category: str = None) -> List[Dict]:
        """
        Поиск локаций в TripAdvisor
        
        Args:
            search_query: Поисковый запрос
            category: Категория (attractions, restaurants, hotels)
            
        Returns:
            List[Dict]: Список найденных локаций
        """
        print(f"{EMOJIS['search']} {MESSAGES['searching'].format(query=search_query)}")
        
        params = {
            "name": "search_locations",
            "arguments": {
                "searchQuery": search_query,
                "language": self.default_language
            }
        }
        
        if category:
            params["arguments"]["category"] = category
        
        response = self.send_request("tools/call", params)
        return self._parse_search_results(response)
    
    def search_nearby_locations(self, latitude: float, longitude: float, category: str = None, search_query: str = None) -> List[Dict]:
        """
        Поиск локаций рядом с координатами (через search_locations с latLong)
        
        ВНИМАНИЕ: Используем обходной путь из-за бага в search_nearby_locations
        
        Args:
            latitude: Широта
            longitude: Долгота
            category: Категория поиска
            search_query: Поисковый запрос
            
        Returns:
            List[Dict]: Список найденных локаций
        """
        print(f"{EMOJIS['location']} {MESSAGES['searching_nearby'].format(lat=latitude, lon=longitude)}")
        
        # Автоматически генерируем searchQuery если не указан
        if not search_query:
            if category:
                search_query = f"{category} near me"
            else:
                search_query = "places near me"
        
        # ОБХОДНОЙ ПУТЬ: используем search_locations с latLong параметром
        # Формат latLong: "latitude,longitude"
        lat_long_str = f"{latitude},{longitude}"
        
        params = {
            "name": "search_locations",  # НЕ search_nearby_locations!
            "arguments": {
                "searchQuery": search_query,
                "latLong": lat_long_str,   # Координаты в формате строки
                "language": self.default_language
            }
        }
        
        if category:
            params["arguments"]["category"] = category
        
        response = self.send_request("tools/call", params)
        return self._parse_search_results(response)
    
    def get_location_details(self, location_id: str) -> Dict:
        """
        Получение детальной информации о локации
        
        Args:
            location_id: ID локации в TripAdvisor
            
        Returns:
            Dict: Детальная информация
        """
        params = {
            "name": "get_location_details",
            "arguments": {
                "locationId": location_id,
                "language": self.default_language
            }
        }
        
        response = self.send_request("tools/call", params)
        return self._parse_detail_response(response)
    
    def get_location_reviews(self, location_id: str) -> List[Dict]:
        """
        Получение отзывов о локации
        
        Args:
            location_id: ID локации
            
        Returns:
            List[Dict]: Список отзывов
        """
        params = {
            "name": "get_location_reviews",
            "arguments": {
                "locationId": location_id,
                "language": self.default_language
            }
        }
        
        response = self.send_request("tools/call", params)
        return self._parse_reviews_response(response)
    
    def _parse_search_results(self, response: Dict) -> List[Dict]:
        """Парсинг результатов поиска"""
        try:
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]
                if isinstance(content.get("json"), dict):
                    return content["json"].get("data", [])
            return []
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка парсинга результатов: {e}")
            return []
    
    def _parse_detail_response(self, response: Dict) -> Dict:
        """Парсинг детальной информации"""
        try:
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]
                if isinstance(content.get("json"), dict):
                    return content["json"]
            return {}
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка парсинга деталей: {e}")
            return {}
    
    def _parse_reviews_response(self, response: Dict) -> List[Dict]:
        """Парсинг отзывов"""
        try:
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]
                if isinstance(content.get("json"), dict):
                    return content["json"].get("data", [])
            return []
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка парсинга отзывов: {e}")
            return []
    
    def stop_server(self):
        """Остановка сервера"""
        if self.process:
            self.process.terminate()
            print(f"{EMOJIS['stop']} {MESSAGES['server_stopped']}")
            self.process = None