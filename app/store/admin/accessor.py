import typing
from hashlib import sha256
from typing import Optional

from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest
from sqlalchemy import desc

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
        admin = await db.select([AdminModel.id, AdminModel.email]) \
            .where(AdminModel.email == email) \
            .gino.first()

        if admin:
            return admin.to_dc()
            # raise HTTPConflict

        admin_last_id = await db.select([AdminModel.id]).order_by(AdminModel.id.desc()).gino.first()
        obj: AdminModel
        if admin_last_id:
            last_id = admin_last_id.id
            last_id = int(last_id) + 1
            obj = await AdminModel.create(
                id=str(last_id),
                email=email,
                password=sha256(password.encode()).hexdigest()
            )
        else:
            last_id = 0
            obj = await AdminModel.create(
                id=str(int(last_id)),
                email=email,
                password=sha256(password.encode()).hexdigest()
            )

        obj.id = int(last_id)
        return obj.to_dc()

    async def get_by_email(self, email: str) -> Optional[Admin]:
        obj = await AdminModel.query.where(AdminModel.email == email).gino.first()
        return None if obj is None else obj.to_dc()

    # async def list_admins(self):
    #     obj = await AdminModel.query.where().gino.all()
