from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from app.store.database.gino import db


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])


class AdminModel(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(), nullable=False)
    password = db.Column(db.Unicode(), nullable=False)

    def to_dc(self):
        return Admin(
            id=self.id,
            email=self.email,
            password=self.password
        )
