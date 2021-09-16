import typing
from logging import getLogger
from app.store.database.gino import db


if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        # await self.app.database.connect()
        return

    async def disconnect(self, app: "Application"):
        # await self.app.database.disconnect()
        pass
