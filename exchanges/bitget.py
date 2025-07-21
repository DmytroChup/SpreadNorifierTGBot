import json
import websockets
import asyncio
from logger_factory import LoggerFactory


class BitgetClient:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price = None
        self.logger = LoggerFactory.create_logger('Bitget', 'logs/bitget.log')

    async def connect(self):
        while True:
            try:
                uri = "wss://ws.bitget.com/v2/ws/public"
                self.logger.info(f"Подключение к Bitget WebSocket ({self.symbol})")
                
                async with websockets.connect(uri) as websocket:
                    sub = {
                        "op": "subscribe",
                        "args": [
                            {"instType": "USDT-FUTURES",
                             "channel": "ticker",
                             "instId": self.symbol}
                        ]
                    }
                    await websocket.send(json.dumps(sub))
                    self.logger.debug(f"Отправлен запрос на подписку: {sub}")

                    async for msg in websocket:
                        data = json.loads(msg)
                        self.logger.debug(f"Получены данные: {data}")
                        
                        try:
                            price = float(data["data"][0]["lastPr"])
                            self.price = price
                            self.logger.info(f"Обновлена цена: {self.price}")
                        except (KeyError, ValueError) as e:
                            self.logger.warning(f"Не удалось извлечь цену из сообщения: {e}")
                            self.logger.debug(f"Проблемное сообщение: {data}")
                            
            except websockets.exceptions.ConnectionClosed:
                self.logger.error("Соединение с Bitget WebSocket закрыто. Переподключение...")
                await asyncio.sleep(2)
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка декодирования JSON: {e}")
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка: {str(e)}")
                await asyncio.sleep(2)