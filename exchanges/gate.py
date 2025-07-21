import json
import websockets
import asyncio
import time
from logger_factory import LoggerFactory


class GateClient:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price = None
        self.logger = LoggerFactory.create_logger('Gate', 'logs/gate.log')

    async def connect(self):
        while True:
            try:
                uri = "wss://fx-ws.gateio.ws/v4/ws/usdt"
                self.logger.info(f"Подключение к Gate WebSocket ({self.symbol})")

                async with websockets.connect(uri) as websocket:
                    sub = {
                        "time": int(time.time()),
                        "channel": "futures.tickers",
                        "event": "subscribe",
                        "payload": [self.symbol]
                    }
                    await websocket.send(json.dumps(sub))
                    self.logger.debug(f"Отправлен запрос на подписку: {sub}")

                    async for msg in websocket:
                        data = json.loads(msg)
                        self.logger.debug(f"Получены данные: {data}")

                        try:
                            if data.get("event") == "update":
                                payload = data["result"][0]
                                self.price = float(payload["last"])
                                self.logger.info(f"Обновлена цена: {self.price}")

                            elif data.get("event") == "subscribe":
                                self.logger.info(f"Успешно подписались на {self.symbol}")

                            else:
                                self.logger.warning(f"Неизвестное событие: {data.get('event')}")

                        except (KeyError, ValueError, IndexError) as e:
                            self.logger.warning(f"Не удалось извлечь цену из сообщения: {e}")
                            self.logger.debug(f"Проблемное сообщение: {data}")

            except websockets.exceptions.ConnectionClosed:
                self.logger.error("Соединение с Gate WebSocket закрыто. Переподключение...")
                await asyncio.sleep(2)
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка декодирования JSON: {e}")
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка: {str(e)}")
                await asyncio.sleep(2)