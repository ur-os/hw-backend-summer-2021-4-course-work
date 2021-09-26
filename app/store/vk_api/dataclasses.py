from dataclasses import dataclass


@dataclass
class UpdateObject:
    id: int
    date: int
    user_id: int
    body: str


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    user_id: int
    text: str
