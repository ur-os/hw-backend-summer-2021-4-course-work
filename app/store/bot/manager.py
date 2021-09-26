import typing
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        if updates:
            for update in updates:
                if update.type == 'message_new':
                    if update.object.body == "/start":
                        await self.start_game(update=update)
                        break
                    if update.object.body == "/best_startup":
                        await self.ping(update=update)
                        break
                    if update.object.body == "/finish":
                        await self.finish_game(update=update)
                        break

                await self.app.store.vk_api.send_message(
                                        Message(
                                            user_id=update.object.user_id,
                                            text="/help <br> команда \"Рука помощи\"",
                                        )
                                    )

    async def ping(self, update: Update):
        await self.app.store.vk_api.send_message(
            Message(
                user_id=update.object.user_id,
                text="P%26%230822%3Bi%26%230822%3Be%26%23"
                     "0822%3Bd%26%230822%3B%20%26%230822%3BP%26%230822%3Bi%26%2308"
                     "22%3Bp%26%230822%3Be%26%230822%3Br%26%230822%3B KTS Studio",
            )
        )

    async def start_game(self, update: Update):
        session = await self.app.store.quizzes.get_game_session_by_user(update.object.user_id)

        # TODO: if time expired

        if session:
            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    text="Игра ещё идёт<br>"
                         "Чтобы завершить игру введите /finish<br>"
                         "Или обратитесь к системному администратору (err 1)",
                )
            )
            return

        game_session = await self.app.store.quizzes.create_game_session(
            state="started",
            user_id=update.object.user_id
        )

        await self.app.store.vk_api.send_message(
            Message(
                user_id=update.object.user_id,
                text="Ого, ты прошёл этот баг"

            )
        )

        if game_session:
            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    text="Игра сейчас начнётся, мой дорогой "
                         + str(game_session.user_id) +
                         "!<br>"
                         "Тебе предстоит выбрать:<br>"
                         "1. Продолжительность игры<br>"
                         "2. Вопрос, из предложенных<br>"
                         "Если что-то непронято --  обратитесь к системному администратору",
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
