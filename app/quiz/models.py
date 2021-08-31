from dataclasses import dataclass
from typing import Optional

from app.store.database.gino import db


@dataclass
class Theme:
    id: Optional[int]
    title: str

# TODO
# Дописать все необходимые поля модели
class ThemeModel(db.Model):
    __tablename__ = "themes"

# TODO
# Дописать все необходимые поля модели
class AnswerModel(db.Model):
    __tablename__ = "answers"



@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]

# TODO
# Дописать все необходимые поля модели
class QuestionModel(db.Model):
    __tablename__ = "questions"


@dataclass
class Answer:
    title: str
    is_correct: bool
