from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Theme,
    Question,
    Answer,
    GameState,
    ThemeModel,
    QuestionModel,
    AnswerModel,
    GameStateModel
)
from typing import List


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        obj = await ThemeModel.create(title=title)
        return obj.to_dc()

    async def create_game_session(self, state: str, user_id: int) -> GameState:
        obj = await GameStateModel.create(
            state=state,
            user_id=user_id,
        )
        return obj.to_dc()

    async def get_game_session_by_user(self, user_id: int) -> Optional[GameState]:
        obj = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        return None if obj is None else obj.to_dc()

    async def delete_game_session_by_user(self, user_id: int):
        game = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        status = await game.delete()
        return status

    async def set_game_session_theme(self, user_id: int, theme: str):
        game = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        status = await game.update(theme=theme)
        return status

    async def set_game_session_date(self, user_id: int, date: int):
        game = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        status = await game.update(date=date)
        return status

    async def set_game_session_state(self, user_id: int, state: str):
        game = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        status = await game.update(state=state)
        return status

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        obj = await ThemeModel.query.where(ThemeModel.title == title).gino.first()
        return None if obj is None else obj.to_dc()

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        obj = await ThemeModel.get(id_)
        return None if obj is None else obj.to_dc()

    async def list_themes(self) -> List[Theme]:
        objs = await ThemeModel.query.gino.all()
        return [o.to_dc() for o in objs]

    async def create_answers(self, question_id, answers: List[Answer]):
        await AnswerModel.insert().gino.all(
            [
                {
                    'title': a.title,
                    'is_correct': a.is_correct,
                    'question_id': question_id

                }
                for a in answers
            ]
        )

    async def create_question(
            self, title: str, theme_id: int, answers: List[Answer]
    ) -> Question:
        obj = await QuestionModel.create(title=title, theme_id=theme_id)
        question = obj.to_dc()
        await self.create_answers(question.id, answers)
        question.answers = answers

        return question

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        query = QuestionModel.outerjoin(
            AnswerModel,
            QuestionModel.id == AnswerModel.question_id,
        )

        query = query.select().where(QuestionModel.title == title)
        questions = await query.gino.load(
            QuestionModel.distinct(QuestionModel.id).load(add_answer=AnswerModel.load())
        ).all()

        if len(questions) == 0 or not questions:
            return None

        return questions[0].to_dc()

    async def list_questions(self) -> List[Question]:
        query = QuestionModel.outerjoin(
            AnswerModel,
            QuestionModel.id == AnswerModel.question_id,
        ).select()

        query = await query.gino.load(
            QuestionModel.distinct(QuestionModel.id).load(add_answer=AnswerModel.load())
        ).all()

        objs = query

        return [o.to_dc() for o in objs]

