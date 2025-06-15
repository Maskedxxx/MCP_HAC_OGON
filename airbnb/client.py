# airbnb/client.py
"""
Клиент для работы с Airbnb MCP сервером
"""

import subprocess
import json
from typing import Dict, List, Any, Optional
from .config import MCP_SERVER_COMMAND, DEFAULT_SEARCH_PARAMS, MESSAGES
from config import EMOJIS


class MCPClient:
    """Клиент для взаимодействия с Airbnb MCP сервером"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.process: Optional[subprocess.Popen] = None
        
    def start_server(self) -> bool:
        """
        Запуск MCP сервера
        
        Returns:
            bool: True если сервер успешно запущен
        """
        print(f"{EMOJIS['start']} {MESSAGES['starting_server']}")
        
        try:
            self.process = subprocess.Popen(
                MCP_SERVER_COMMAND,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Ждем пока сервер запустится
            startup_line = self.process.stderr.readline()
            print(f"{EMOJIS['success']} {startup_line.strip()}")
            return True
            
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка запуска сервера: {e}")
            return False
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправка запроса к MCP серверу
        
        Args:
            method: Метод для вызова
            params: Параметры запроса
            
        Returns:
            Dict: Ответ от сервера
        """
        if not self.process:
            raise RuntimeError("Сервер не запущен")
            
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
        return json.loads(response_line)
    
    def search_accommodations(self, location: str, **kwargs) -> List[Dict]:
        """
        Поиск жилья в указанном месте
        
        Args:
            location: Город для поиска
            **kwargs: Дополнительные параметры (adults, checkin, checkout и т.д.)
            
        Returns:
            List[Dict]: Список найденных вариантов жилья
        """
        # Объединяем параметры по умолчанию с переданными
        search_params = {**DEFAULT_SEARCH_PARAMS, **kwargs}
        adults = search_params.get("adults", 2)
        
        print(f"{EMOJIS['search']} {MESSAGES['searching'].format(location=location, adults=adults)}")
        
        # Подготавливаем параметры для API
        api_params = {
            "name": "airbnb_search",
            "arguments": {
                "location": location,
                **search_params
            }
        }
        
        response = self.send_request("tools/call", api_params)
        
        if "result" in response and not response.get("result", {}).get("isError", False):
            data = json.loads(response["result"]["content"][0]["text"])
            return data.get("searchResults", [])
        else:
            print(f"{EMOJIS['error']} Ошибка поиска")
            return []
    
    def get_listing_details(self, listing_id: str) -> Dict:
        """
        Получение детальной информации о листинге
        
        Args:
            listing_id: ID листинга
            
        Returns:
            Dict: Детальная информация о листинге
        """
        print(f"{EMOJIS['details']} {MESSAGES['getting_details'].format(listing_id=listing_id)}")
        
        params = {
            "name": "airbnb_listing_details",
            "arguments": {"id": listing_id}
        }
        
        response = self.send_request("tools/call", params)
        
        if "result" in response:
            data = json.loads(response["result"]["content"][0]["text"])
            return data
        return {}
    
    def stop_server(self):
        """Остановка сервера"""
        if self.process:
            self.process.terminate()
            print(f"{EMOJIS['stop']} {MESSAGES['server_stopped']}")
            self.process = None