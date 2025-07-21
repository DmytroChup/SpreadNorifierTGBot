import json
import websockets
import asyncio
import uuid
import gzip
from logger_factory import LoggerFactory


class BingXClient:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price = None
        self.logger = LoggerFactory.create_logger('BingX', 'logs/bingx.log')

    async def connect(self):
        while True:
            try:
                uri = "wss://open-api-swap.bingx.com/swap-market"
                self.logger.info(f"Подключение к BingX WebSocket ({self.symbol})")

                async with websockets.connect(uri) as websocket:
                    sub_id = str(uuid.uuid4())
                    sub = {
                        "id": sub_id,
                        "reqType": "sub",
                        "dataType": f"{self.symbol}@ticker"
                    }
                    await websocket.send(json.dumps(sub))
                    self.logger.debug(f"Отправлен запрос на подписку: {sub}")

                    async for msg in websocket:
                        try:
                            decompressed_data = gzip.decompress(msg).decode("utf-8")
                            data = json.loads(decompressed_data)
                            self.logger.debug(f"Получены данные: {data}")

                            try:
                                if "data" in data and "c" in data["data"]:
                                    price = float(data["data"]["c"])
                                    self.price = price
                                    self.logger.info(f"Обновлена цена: {self.price}")
                            except (KeyError, ValueError) as e:
                                self.logger.warning(f"Не удалось извлечь цену из сообщения: {e}")
                                self.logger.debug(f"Проблемное сообщение: {data}")

                        except Exception as e:
                            self.logger.error(f"Ошибка при обработке сообщения: {e}")

            except websockets.exceptions.ConnectionClosed:
                self.logger.error("Соединение с BingX WebSocket закрыто. Переподключение...")
                await asyncio.sleep(2)
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка декодирования JSON: {e}")
                await asyncio.sleep(2)
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка: {str(e)}")
                await asyncio.sleep(2)