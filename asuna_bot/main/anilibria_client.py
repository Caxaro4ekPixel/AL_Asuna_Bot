import asyncio
from anilibria import AniLibriaClient
from orjson import JSONDecodeError
from aiohttp import WSServerHandshakeError
from loguru import logger as log

class ALClient(AniLibriaClient):
    async def astart(self, *, auto_reconnect: bool = True):
        """
        Запускает клиент асинхронно (ignore JSONDecodeError)
        """

        while True:
            try:
                await self._websocket.start()
            except (WSServerHandshakeError, JSONDecodeError) as error:
                if auto_reconnect:
                    log.error(error)
                    log.debug("Websocket disconnected. Reconnecting...")
                    continue
                raise error from error
            except (KeyboardInterrupt, asyncio.CancelledError):
                await self.close()
                break

al_client = ALClient(logging=False)