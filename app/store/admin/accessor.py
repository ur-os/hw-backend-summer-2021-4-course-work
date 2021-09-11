import base64
import typing
from hashlib import sha256
from random import random
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin, AdminModel
from app.store.database.database import db

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)
        await self.create_admin(
            email=app.config.admin.email,
            password=app.config.admin.password
        )

    async def create_admin(self, email: str, password: str) -> Admin:
        _id = None
        query = db.select([AdminModel])
        rows = await query.gino.all()

        if not rows:
            _id = 1
        if rows:
            _id = str(int(rows[0]['id']) + 1)

        return await AdminModel.create(
            id=str(_id),
            email=email,
            password=sha256(password.encode()).hexdigest()
        )

    async def get_by_email(self, email: str) -> Optional[Admin]:
        obj = await AdminModel.query.where(AdminModel.email == email).gino.first()
        return None if obj is None else obj.to_dc()
