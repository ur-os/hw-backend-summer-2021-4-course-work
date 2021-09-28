from datetime import datetime
import random
import typing
from logging import getLogger
from typing import Optional

from app.quiz.models import GameState, Player, Score, Game, Question, Answer
from app.store.vk_api.dataclasses import Update, Message
from app.store.bot.utils import to_string, to_datetime, int_to_datetime, days_hours_minutes

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self.commands = [
            "/start",
            "/finish",
            "/best_startup",
            "/help",
            "/score",
        ]

    async def handle_updates(self, updates: list[Update]):
        if updates:
            for update in updates:
                if update.type == 'message_new':

                    if update.object.body in self.commands:
                        if update.object.body == "/start":
                            await self.start_game(update=update)
                            break
                        if update.object.body == "/best_startup":
                            await self.ping(update=update)
                            break
                        if update.object.body == "/score":
                            await self.show_score(update=update)
                            break
                        if update.object.body == "/finish":
                            await self.finish_game(update=update)
                            break
                        if update.object.body == "/help":
                            await self.help(update=update)
                            break

                    game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
                    if game:
                        await self.if_game_started(update=update, game=game)
                        break

                await self.response(update, "/help <br> команда \"Рука помощи\"")

    async def ping(self, update: Update):
        await self.app.store.vk_api.send_message_chat(
            Message(
                user_id=update.object.user_id,
                peer_id=update.object.peer_id,
                text="P%26%230822%3Bi%26%230822%3Be%26%23"
                     "0822%3Bd%26%230822%3B%20%26%230822%3BP%26%230822%3Bi%26%2308"
                     "22%3Bp%26%230822%3Be%26%230822%3Br%26%230822%3B KTS Studio",
            )
        )
        members = await self.app.store.vk_api.get_members(update.object.peer_id)
        print(members)

    async def start_game(self, update: Update):
        game = await self.create_game(update=update)
        await self.choose_theme(update=update)
        return

    async def finish_game(self, update: Update):
        await self.show_score(update=update)
        await self.delete_game(update=update)
        return

    async def if_game_started(self, update: Update, game: Game):
        game_state = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)
        if game_state.start_time:
            start_time = to_datetime(game_state.start_time)
            expired_time = start_time + int_to_datetime(game_state.date)
            time_now = datetime.now()
            delta_time = days_hours_minutes(expired_time - time_now)
            if time_now > expired_time:
                await self.show_score(update=update)
                await self.finish_game(update=update)

        if game_state.state == "in_process":
            await self.to_answer(update=update)
        if game_state.state == "round_ended":
            await self.new_round(update=update, game=game, game_state=game_state)

        theme = game_state.theme
        if not theme:
            themes = await self.available_themes(update=update)
            if update.object.body in themes:

                status = await self.app.store.quizzes.set_game_session_theme(
                    game_id=game.id,
                    theme=update.object.body
                )
                if status:
                    await self.response_chat(
                        update=update,
                        text="Выбрана тема<br>"
                             + update.object.body +
                             "<br>Выберите длительность игры<br>1<br>2<br>5<br>минут",
                    )
                    return
                await self.response(update, "Тема не выбрана")
                return
            await self.response(update, "Тема не найдена, скопируйте название темы из нашего чата")
            return

        if not game_state.date:  # how long the game has been going
            if int(update.object.body) in [1, 2, 5]:
                status = await self.app.store.quizzes.set_game_session_date(
                    game_id=game.id,
                    date=int(update.object.body)
                )

                if status:
                    await self.response_chat(
                        update=update,
                        text="Выбрана продолжительность: "
                             + str(update.object.body) +
                             "<br>"
                             "А вот и твой первый вопрос:",
                    )

                question = await self.get_random_new_question(update=update)
                await self.send_question(
                    update=update,
                    question=question
                )
                await self.app.store.quizzes.set_game_session_question(
                    game_id=game.id,
                    question=question
                )

                await self.app.store.quizzes.set_game_session_start_date(
                    game_id=game.id,
                    start_time=to_string(datetime.now())
                )
                await self.app.store.quizzes.set_game_session_state(
                    game_id=game.id,
                    state="in_process"
                )

                return
            await self.response(update, "Продолжительность не найдена, мы можем только 1, 2 и 5 минут")
            return

    async def help(self, update: Update):
        await self.response_chat(
            update,
            "Список доступных команд:<br>"
            "/start -- начать игру<br>"
            "/finish -- закончить игру<br>"
            "/score -- текущий счёт игроков<br>"
            "/best_startup -- пасхалочка<br>"
            "/help -- введи ещё раз, давай<br>"
        )

    async def response(self, update: Update, text: str):
        await self.app.store.vk_api.send_message(
            Message(
                user_id=update.object.user_id,
                text=text,
            )
        )

    async def response_chat(self, update: Update, text: str):
        await self.app.store.vk_api.send_message_chat(
            Message(
                user_id=update.object.user_id,
                peer_id=update.object.peer_id,
                text=text,
            )
        )

    async def get_new_questions_str(self, update: Update) -> list[str]:
        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
        answered_questions = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)
        theme = answered_questions.theme

        all_questions = await self.app.store.quizzes.list_questions_via_theme(theme)
        all_questions = set([x.title for x in all_questions])

        answered_questions = set(
            list(answered_questions.answered_questions.values()))  # dict as list (keys have no meaning)

        new_questions = list(all_questions - answered_questions)

        return new_questions

    async def get_random_new_question(self, update: Update) -> str:
        questions = await self.get_new_questions_str(update)
        return questions[random.randint(0, len(questions))]

    async def create_game(self, update: Update) -> Optional[Game]:
        is_exist = await self.is_game_exist(update=update)
        if is_exist:
            await self.response_chat(update=update, text="Игра существует<br>/finish -- завершить")
            return None

        game = await self.app.store.quizzes.create_game(update.object.peer_id)
        game_state = await self.app.store.quizzes.create_game_session("started", game.id)
        await self.response_chat(update=update, text="Игра создана<br>Участники:<br>")

        chat_members = await self.app.store.vk_api.get_members(update.object.peer_id)
        player_table = str()
        for member in chat_members:

            player = await self.app.store.quizzes.create_player(
                game_id=game.id,
                user_id=member.user_id,
                name=member.first_name + " " + member.last_name
            )
            if not player:
                await self.response_chat(update=update, text="Игрок " + str(player.user_id) + " не создан")
                break

            score = await self.app.store.quizzes.create_score(
                game_id=game.id,
                player_id=player.id,
                score=0
            )
            if not score:
                await self.response_chat(update=update, text="Счёт для " + str(player.user_id) + " не создан")
                break

            player_table += player.name + " -- " + str(score.score) + "<br>"
        await self.response_chat(update=update, text=player_table)
        return game

    async def delete_game(self, update: Update):
        is_exist = await self.is_game_exist(update=update)
        if not is_exist:
            await self.response_chat(update=update, text="Игра не существует<br>/start -- начать")
            return

        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
        status = await self.app.store.quizzes.delete_game_by_id(game_id=game.id)
        if status:
            await self.response_chat(update=update, text="Игра удалена<br>/start -- начать")

    async def members_list(self, update: Update) -> list[str]:
        chat_members = await self.app.store.vk_api.get_members(update.object.peer_id)
        return [member.last_name + " " + member.last_name for member in chat_members]

    async def is_game_exist(self, update: Update) -> bool:
        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)

        if game:
            game_state = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)
            if game_state:
                await self.response_chat(
                    update=update,
                    text="Игра ещё идёт<br>"
                         "Чтобы завершить игру введите /finish<br>"
                         "Или обратитесь к системному администратору")

                return True
        return False

    async def choose_theme(self, update: Update):
        unanswered = await self.available_themes(update=update)

        themes_str = str()
        for theme in unanswered:
            themes_str += theme + "<br>"
        await self.response_chat(update, "Выберите тему:<br>" + themes_str)

    async def available_themes(self, update: Update) -> list[str]:
        themes = await self.app.store.quizzes.list_themes()
        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
        game_state = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)

        answered = set(list(game_state.answered.values()))
        all_themes = set([themes.title for themes in themes])

        return list(all_themes - answered)

    async def available_questions(self, update: Update, theme: str) -> list[str]:
        questions = await self.app.store.quizzes.list_questions_via_theme(theme)
        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
        game_state = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)

        answered = set(list(game_state.answered_questions.values()))
        all_questions = set([question.title for question in questions])

        return list(all_questions - answered)

    async def send_question(self, update: Update, question: str):
        question = await self.app.store.quizzes.get_question_by_title(question)
        text = "Вопрос:<br>" + question.title + "<br><br>Ответы:<br>"
        answers = question.answers
        for answer in answers:
            text += answer.title + "<br>"
        await self.response_chat(update=update, text=text)

    async def show_score(self, update: Update, ):
        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
        game_state = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)
        players = await self.app.store.quizzes.list_players(game_id=game.id)

        tablescore = ""
        time = ""
        if game_state.start_time:
            start_time = to_datetime(game_state.start_time)
            expired_time = start_time + int_to_datetime(game_state.date)
            time_now = datetime.now()
            delta_time = str(days_hours_minutes(expired_time - time_now))

            time = "Осталось времени: " + delta_time + "<br><br>"
        tablescore += time

        for player in players:
            scores = await self.app.store.quizzes.get_scores_by_player_id(player_id=player.id)
            for score in scores:
                if score.game_id == game.id:
                    tablescore += player.name + " -- " + str(score.score) + "<br>"

        await self.response_chat(update, tablescore)

    async def to_answer(self, update: Update):
        game = await self.app.store.quizzes.get_game_by_chat_id(update.object.peer_id)
        game_state = await self.app.store.quizzes.get_game_session_by_game_id(game_id=game.id)

        players = await self.app.store.quizzes.get_players_id_by_user_id(update.object.user_id)
        player: Player
        for p in players:
            if p.game_id == game.id:
                player = p
                break
        if not Player:
            await self.response_chat(update, "Кто говорит? Откуда звук? Пользователь потерялся")

        current_question = await self.app.store.quizzes.get_question_by_title(game_state.question)
        right_answer = ""
        for answer in current_question.answers:
            if answer.is_correct:
                right_answer = answer.title
                break

        if update.object.body == right_answer:
            user_id = update.object.user_id
            current_score = 0
            current_scores = await self.app.store.quizzes.get_scores_by_player_id(player_id=player.id)
            for score in current_scores:
                if score.game_id == game.id:
                    current_score = score.score

            current_score += 1

            await self.app.store.quizzes.set_player_score(player_id=player.id, scores=current_score)
            await self.response_chat(update, text=str(player.name) + " дал правильный ответ!")

        else:
            await self.response_chat(
                update=update,
                text=str(player.name)
                     + " дал неверный ответ!<br>Правильный ответ: " +
                     right_answer
            )
        await self.app.store.quizzes.set_game_session_state(game_id=game.id, state="round_ended")
        await self.app.store.quizzes.archive_question(game_id=game.id)
        questions = await self.available_questions(update=update, theme=game_state.theme)
        if not questions:
            await self.app.store.quizzes.archive_theme(game_id=game.id)
        await self.show_available_themes(update=update)

    async def show_available_themes(self, update: Update):
        themes = await self.available_themes(update=update)
        text = "Выберите тему:<br>"

        for theme in themes:
            text += theme + "<br>"

        await self.response_chat(update, text)

    async def new_round(self, update: Update, game: Game, game_state: GameState):
        themes = await self.available_themes(update=update)
        if not themes:
            await self.finish_game(update=update)

        if update.object.body in themes:
            await self.app.store.quizzes.set_game_session_theme(game_id=game.id, theme=update.object.body)

            question = await self.get_random_new_question(update=update)
            await self.response_chat(update, "А вот и твой новый вопрос:<br>")
            await self.send_question(update=update, question=question)

            await self.app.store.quizzes.set_game_session_question(
                game_id=game.id,
                question=question
            )
        else:
            await self.response_chat(update, "Такой темы не существует<br>")
        await self.app.store.quizzes.set_game_session_state(game_id=game.id, state="in_process")