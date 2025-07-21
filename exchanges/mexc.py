import json
import websockets
import asyncio
from logger_factory import LoggerFactory


class MEXCClient:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price = None
        self.logger = LoggerFactory.create_logger('MEXC', 'logs/mexc.log')

    async def connect(self):
        while True:
            try:
                uri = "wss://contract.mexc.com/edge"
                self.logger.info(f"Подключение к MEXC WebSocket ({self.symbol})")

                async with websockets.connect(uri) as websocket:
                    sub = {
                        "method": "sub.ticker",
                        "param": {
                            "symbol": self.symbol
                        }
                    }
                    await websocket.send(json.dumps(sub))
                    self.logger.debug(f"Отправлен запрос на подписку: {sub}")

                    async for msg in websocket:
                        data = json.loads(msg)
                        self.logger.debug(f"Получены данные: {data}")

                        if "data" in data and isinstance(data["data"], dict):
                            last = float(data["data"]["lastPrice"])
                            self.price = last
                            self.logger.info(f"Обновлена цена: {self.price}")
                        else:
                            self.logger.warning(f"Получено сообщение без сделки: {data}")

            except websockets.exceptions.ConnectionClosed:
                self.logger.error("Соединение с MEXC WebSocket закрыто. Переподключение...")
                await asyncio.sleep(2)
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка декодирования JSON: {e}")
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка: {str(e)}")
                await asyncio.sleep(2)