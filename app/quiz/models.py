from dataclasses import dataclass
from typing import Optional, List

from app.store.database.gino import db
from gino.dialects.asyncpg import JSONB  # the same as in sqlalchemy
from enum import Enum

@dataclass
class Theme:
    id: Optional[int]
    title: str


# TODO
# Дописать все необходимые поля модели
class ThemeModel(db.Model):
    __tablename__ = "themes"

    id = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)

    def to_dc(self):
        return Theme(**self.to_dict())



@dataclass
class Answer:
    title: str
    is_correct: bool


class AnswerModel(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    is_correct = db.Column(db.Boolean(), nullable=False)
    question_id = db.Column(
        db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False
    )

    def to_dc(self):
        return Answer(title=self.title, is_correct=self.is_correct)


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]


class QuestionModel(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    theme_id = db.Column(
        db.ForeignKey('themes.id', ondelete='CASCADE'), nullable=False
    )

    def __init__(self, **kw):
        super().__init__(**kw)
        self._answers: List[AnswerModel] = list()

    def to_dc(self):
        return Question(
            id=self.id,
            title=self.title,
            theme_id=self.theme_id,
            answers=[a.to_dc() for a in self._answers]
        )

    @property
    def add_answer(self) -> List[AnswerModel]:
        return self._answers

    @add_answer.setter
    def add_answer(self, val: AnswerModel):
        self._answers.append(val)


@dataclass
class GameState:
    id: int
    state: str
    theme: str
    date: int
    start_date: int
    user_id: int
    answered: dict


class GameStateModel(db.Model):
    __tablename__ = "game_states"

    class StateEnum(Enum):  # for gino/alchemy enum schema
        STARTED = 'started'
        FINISHED = 'finished'

    id = db.Column(db.BigInteger(), primary_key=True, unique=True, autoincrement=True)
    state = db.Column(db.String(), nullable=False)
    theme = db.Column(db.String(), nullable=True)
    date = db.Column(db.BigInteger(), nullable=True)  # how long the game been going (default time dimension)
    start_date = db.Column(db.BigInteger(), nullable=True)  # (default time dimension)
    user_id = db.Column(db.BigInteger(), nullable=False)
    answered = db.Column(JSONB, server_default="{}")

    def to_dc(self):
        return GameState(
            id=self.id,
            state=self.state,
            theme=self.theme,
            date=self.date,
            start_date=self.start_date,
            user_id=self.user_id,
            answered=self.answered
        )