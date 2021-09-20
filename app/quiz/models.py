from dataclasses import dataclass
from typing import Optional, List

from app.store.database.gino import db


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
    theme: str
    duration: int
    used_questions: list["Question"]

class GameStateModel(db.Model):
    __tablename__ = "game_states"

    id = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    theme_id = db.Column(
        db.ForeignKey('themes.id', ondelete='CASCADE'), nullable=False
    )