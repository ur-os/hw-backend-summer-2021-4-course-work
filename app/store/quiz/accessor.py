from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Theme,
    Question,
    Answer,
    ThemeModel,
    QuestionModel,
    AnswerModel,
)
from typing import List


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        obj = await ThemeModel.create(title=title)
        return obj.to_dc()

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

    async def _get_questions_join(self):
        return QuestionModel.outerjoin(
            AnswerModel,
            QuestionModel.id == AnswerModel.question_id,
        ).select()

    async def _get_questions_load(self, query):
        return query.gino.load(
            QuestionModel.distinct(QuestionModel.id).load(add_answer=AnswerModel.load())
        ).all()

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        query = QuestionModel.outerjoin(
            AnswerModel,
            QuestionModel.id == AnswerModel.question_id,
        )
        query = query.select().where(QuestionModel.title == title)
        questions = await query.gino.load(
            QuestionModel.distinct(QuestionModel.id).load(add_answer=AnswerModel.load())
        ).all()

        if len(questions) == 0:
            return None

        return None if questions is None else questions[0].to_dc()

    async def list_questions(self, theme_id: Optional[int] = None) -> List[Question]:
        QuestionModel.outerjoin(
            AnswerModel,
            QuestionModel.id == AnswerModel.question_id,
        ).select()

        query = QuestionModel.outerjoin(
            AnswerModel,
            QuestionModel.id == AnswerModel.question_id,
        ).select()

        query = await query.gino.load(
            QuestionModel.distinct(QuestionModel.id).load(add_answer=AnswerModel.load())
        ).all()

        objs = query

        return [o.to_dc() for o in objs]
