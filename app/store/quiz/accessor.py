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
    GameStateModel,
    GameModel,
    Game,
    PlayerModel,
    Player,
    Score,
    ScoreModel
)
from typing import List


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        obj = await ThemeModel.create(title=title)
        return obj.to_dc()

    async def create_game_session(self, state: str, game_id: int) -> GameState:
        obj = await GameStateModel.create(
            state=state,
            game_id=game_id
        )
        return obj.to_dc()

    async def create_game(self, id_lobby: int) -> Game:
        obj = await GameModel.create(
            id_lobby=id_lobby,
        )
        return obj.to_dc()

    async def create_player(self, game_id: int, user_id: int, name: str) -> Player:
        obj = await PlayerModel.create(
            game_id=game_id,
            user_id=user_id,
            name=name
        )
        return obj.to_dc()

    async def create_score(self, game_id: int, player_id: int, score: int) -> Score:
        obj = await ScoreModel.create(
            game_id=game_id,
            player_id=player_id,
            score=score
        )
        return obj.to_dc()

    async def get_game_session_by_user(self, user_id: int) -> Optional[GameState]:
        obj = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        return None if obj is None else obj.to_dc()

    async def get_game_by_chat_id(self, chat_id: int) -> Optional[Game]:
        obj = await GameModel.query.where(GameModel.id_lobby == chat_id).gino.first()
        return None if obj is None else obj.to_dc()

    async def get_player_by_player_id(self, player_id: int) -> Optional[Player]:
        obj = await PlayerModel.query.where(PlayerModel.player_id == player_id).gino.first()
        return None if obj is None else obj.to_dc()

    async def get_players_id_by_user_id(self, user_id: int) -> Optional[list[Player]]:
        objs = await PlayerModel.query.where(PlayerModel.user_id == user_id).gino.all()
        return [o.to_dc() for o in objs]

    async def get_game_session_by_game_id(self, game_id: int) -> Optional[GameState]:
        obj = await GameStateModel.query.where(GameStateModel.game_id == game_id).gino.first()
        return None if obj is None else obj.to_dc()

    async def delete_game_session_by_user(self, user_id: int):
        game = await GameStateModel.query.where(GameStateModel.user_id == user_id).gino.first()
        status = await game.delete()
        return status

    async def get_scores_by_player_id(self, player_id: int) -> list[Score]:
        objs = await ScoreModel.query.where(ScoreModel.player_id == player_id).gino.all()
        return [o.to_dc() for o in objs]

    async def get_score(self, game_id: int, player_id: int):
        query = ScoreModel.outerjoin(
            PlayerModel,
            ScoreModel.player_id == player_id,
        )
        obj = await query.select().where(ScoreModel.game_id == game_id).gino.first()

        return obj

    async def delete_game_by_id(self, game_id: int):
        game = await GameModel.query.where(GameModel.id == game_id).gino.first()

        status = await game.delete()
        return status


    async def set_game_session_theme(self, game_id: int, theme: str):
        game_state = await GameStateModel.query.where(GameStateModel.game_id == game_id).gino.first()
        status = await game_state.update(theme=theme).apply()
        return status

    async def set_game_session_date(self, game_id: int, date: int):
        game_state = await GameStateModel.query.where(GameStateModel.game_id == game_id).gino.first()
        status = await game_state.update(date=date).apply()
        return status

    async def set_game_session_start_date(self, game_id: int, start_time: str):
        game_state = await GameStateModel.query.where(GameStateModel.game_id == game_id).gino.first()
        print(game_state.id, start_time)
        status = await game_state.update(start_time=start_time).apply()
        print(status)
        return status

    async def set_game_session_question(self, game_id: int, question: str):
        game_state = await GameStateModel.query.where(GameStateModel.game_id == game_id).gino.first()
        status = await game_state.update(question=question).apply()
        return status

    async def set_game_session_state(self, game_id: int, state: str):
        game = await GameStateModel.query.where(GameStateModel.game_id == game_id).gino.first()
        status = await game.update(state=state).apply()
        return status

    async def set_player_score(self, player_id: int, scores: int):
        score = await ScoreModel.query.where(ScoreModel.player_id == player_id).gino.first()
        status = await score.update(score=scores).apply()
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

    async def list_questions_via_theme(self, title: str) -> List[Question]:
        theme = await self.app.store.quizzes.get_theme_by_title(title)
        query = await QuestionModel.query.where(QuestionModel.theme_id == theme.id).gino.all()
        objs = query

        return [o.to_dc() for o in objs]

    async def list_players(self, game_id: int) -> list[Player]:
        objs = await PlayerModel.query.where(PlayerModel.game_id == game_id).gino.all()
        return [o.to_dc() for o in objs]

    async def archive_theme(self, game_id: int):  # game --> game_state?
        game_state = await self.get_game_session_by_game_id(game_id=game_id)
        answered = game_state.theme
        answered_list = game_state.answered
        answered_list[len(answered_list)] = answered

        game_session = await GameStateModel.query.where(GameStateModel.id == game_state.id).gino.first()
        await game_session.update(answered=answered_list).apply()
        # await game_session.update(theme="").apply()

    async def archive_question(self, game_id: int):  # game --> game_state?
        game_state = await self.get_game_session_by_game_id(game_id=game_id)
        answered = game_state.question
        answered_list = game_state.answered_questions
        answered_list[len(answered_list)] = answered

        game_session = await GameStateModel.query.where(GameStateModel.id == game_state.id).gino.first()
        await game_session.update(answered_questions=answered_list).apply()
        # await game_session.update(question="").apply()