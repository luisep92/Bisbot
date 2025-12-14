import asyncio
from DiscordBot import DiscordBot
from Mocks import MockAuthor, MockChannel, MockMessage, MockMessageHandler, MockDiscordBot


async def test_bot_basic_flow():
    bot = MockDiscordBot()
    bot._test_user = MockAuthor("BisbalBot", bot=True, id=999)

    # 🔁 inyectamos mock
    bot.message_handler = MockMessageHandler()

    channel = MockChannel()

    user = MockAuthor("Pepe", bot=False, id=1)

    # Mensaje normal (no debería responder)
    msg1 = MockMessage("hola que tal", user, channel)
    await bot.on_message(msg1)

    # Keyword → debería responder
    msg2 = MockMessage("me flipa bisbal", user, channel)
    await bot.on_message(msg2)

    # Forzamos contador hasta join automático
    for _ in range(9):
        await bot.on_message(MockMessage("spam", user, channel))

    # Este debería disparar el join
    await bot.on_message(MockMessage("ultimo", user, channel))


if __name__ == "__main__":
    asyncio.run(test_bot_basic_flow())
