from dataclasses import dataclass
from typing import Optional, List

from app.store.database.gino import db
from gino.dialects.asyncpg import JSONB  # the same as in sqlalchemy

@dataclass
class Theme:
    id: Optional[int]
    title: str


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
    question: str
    date: int
    start_date: str
    start_time: str
    game_id: int
    answered: dict
    answered_questions: dict


class GameStateModel(db.Model):
    __tablename__ = "game_states"

    id = db.Column(db.BigInteger(), primary_key=True, unique=True, autoincrement=True)
    state = db.Column(db.String(), nullable=False)
    theme = db.Column(db.String(), nullable=True)
    question = db.Column(db.String(), nullable=True)
    date = db.Column(db.BigInteger(), nullable=True)  # how long the game been going (default time dimension)
    start_date = db.Column(db.String(50), nullable=True)  # (default time dimension)
    start_time = db.Column(db.String(128))
    game_id = db.Column(db.ForeignKey('game.id', ondelete='CASCADE'), nullable=True)
    answered = db.Column(JSONB, server_default="{}")
    answered_questions = db.Column(JSONB, server_default="{}")

    def to_dc(self):
        return GameState(
            id=self.id,
            state=self.state,
            theme=self.theme,
            question=self.question,
            date=self.date,
            start_date=self.start_date,
            start_time=self.start_time,
            game_id=self.game_id,
            answered=self.answered,
            answered_questions=self.answered_questions
        )


@dataclass
class Game:
    id: int
    id_lobby: int


@dataclass
class Score:
    id: int
    player_id: int
    game_id: int
    score: int


@dataclass
class Player:
    id: int
    game_id: int
    user_id: int
    name: str


class PlayerModel(db.Model):
    __tablename__ = "player"

    id = db.Column(db.BigInteger(), primary_key=True, unique=True, autoincrement=True)
    game_id = db.Column(db.ForeignKey('game.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.BigInteger(), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def to_dc(self):
        return Player(
            id=self.id,
            game_id=self.game_id,
            user_id=self.user_id,
            name=self.name,
        )


class ScoreModel(db.Model):
    __tablename__ = "score"

    id = db.Column(db.BigInteger(), primary_key=True, unique=True, autoincrement=True)
    player_id = db.Column(db.ForeignKey('player.id'), nullable=True)
    game_id = db.Column(db.ForeignKey('game.id', ondelete='CASCADE'), nullable=True)
    score = db.Column(db.BigInteger())

    def to_dc(self):
        return Score(
            id=self.id,
            player_id=self.player_id,
            game_id=self.game_id,
            score=self.score,
        )


class GameModel(db.Model):
    __tablename__ = "game"

    id = db.Column(db.BigInteger(), primary_key=True, unique=True, autoincrement=True)
    id_lobby = db.Column(db.BigInteger(), unique=True)

    def to_dc(self):
        return Game(
            id=self.id,
            id_lobby=self.id_lobby,
        )

