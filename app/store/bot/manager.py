import random
import typing
from logging import getLogger

from app.quiz.models import GameState
from app.store.vk_api.dataclasses import Update, Message

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
                        if update.object.body == "/finish":
                            await self.finish_game(update=update)
                            break
                        if update.object.body == "/help":
                            await self.help(update=update)
                            break

                    game = await self.app.store.quizzes.get_game_session_by_user(update.object.user_id)
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
        session = await self.app.store.quizzes.get_game_session_by_user(update.object.user_id)

        # TODO: if time expired

        if session:
            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    text="Игра ещё идёт<br>"
                         "Чтобы завершить игру введите /finish<br>"
                         "Или обратитесь к системному администратору",
                )
            )
            return

        game_session = await self.app.store.quizzes.create_game_session(
            state="started",
            user_id=update.object.user_id
        )

        if game_session:
            list_themes = await self.app.store.quizzes.list_themes()
            proposed_themes = ""
            for p in [str(theme.title) + "<br>" for theme in list_themes]:
                proposed_themes += p

            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    text="Игра сейчас начнётся, мой дорогой "
                         + str(game_session.user_id) +
                         "!<br>"
                         "Тебе предстоит ввести:<br>"
                         "1. Тему из предложенных<br>"
                         "2. Продолжительность игры<br>"
                         "Если что-то непронято --  обратитесь к системному администратору<br><br>"
                         "Темы:<br>"
                         + proposed_themes,
                )
            )
            return
        await self.app.store.vk_api.send_message(
            Message(
                user_id=update.object.user_id,
                text="Не удалось создать игру<br>"
                     "Обратитесь к системному администратору"
            )
        )
        return

    async def finish_game(self, update: Update):
        session = await self.app.store.quizzes.get_game_session_by_user(update.object.user_id)

        if session:
            deleted = await self.app.store.quizzes.delete_game_session_by_user(session.user_id)

            if deleted:
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.user_id,
                        text="Игра удалена<br>"
                             "Чтобы начать игру введите /start<br>"
                             "Или обратитесь к системному администратору",
                    )
                )
                return

            if not deleted:
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.user_id,
                        text="Не удалось завершить игру<br>"
                             "Чтобы завершить игру введите /finish<br>"
                             "Или обратитесь к системному администратору",
                    )
                )
                return

        await self.app.store.vk_api.send_message(
            Message(
                user_id=update.object.user_id,
                text="Сессия не найдена<br>"
                     "Чтобы начать игру введите /start<br>"
                     "Или обратитесь к системному администратору",
            )
        )
        return

    async def if_game_started(self, update: Update, game: GameState):
        if not game.theme:

            game_in_store = await self.app.store.quizzes.get_theme_by_title(game.theme)
            if not game_in_store:
                status_theme = await self.app.store.quizzes.set_game_session_theme(
                    user_id=game.user_id,
                    theme=update.object.body
                )

                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.user_id,
                        text="Выбрана тема<br>"
                        + update.object.body +
                        "<br>Выберите длительность игры<br>1<br>2<br>5<br>минут",
                    )
                )
                return
            await self.response(update, "Тема не найдена, скопируйте название темы из нашего чата")
            return

        if not game.date:  # how long the game has been going
            if int(update.object.body) in [1, 2, 5]:
                status_date = await self.app.store.quizzes.set_game_session_date(
                    user_id=game.user_id,
                    date=int(update.object.body)
                )

                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.user_id,
                        text="Выбрана продолжительность: "
                        + update.object.body + "<br>"
                        "А вот и твой первый вопрос:",
                    )
                )

                question = await self.get_random_new_question(update=update)
                await self.response(update=update, text=question)
                return
            await self.response(update, "Продолжительность не найдена, мы можем только 1, 2 и 5 минут")
            return

    async def help(self, update: Update):
        await self.response(
            update,
            "Список доступных команд:<br>"
            "/start -- начать игру<br>"
            "/finish -- закончить игру<br>"
            "/score -- текущий счёт игроков"
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

    async def get_new_questions(self, update: Update) -> list:
        answered = await self.app.store.quizzes.get_game_session_by_user(update.object.user_id)
        theme = answered.theme

        all_questions = await self.app.store.quizzes.list_questions_via_theme(theme)
        all_questions = set([x.title for x in all_questions])

        answered = set(list(answered.answered.values()))  # dict as list (keys have no meaning)

        new_questions = list(all_questions - answered)

        return new_questions

    async def get_random_new_question(self, update: Update):
        questions = await self.get_new_questions(update)
        return questions[random.randint(0, len(questions))]

    async def to_answer(self, update: Update):
        pass


