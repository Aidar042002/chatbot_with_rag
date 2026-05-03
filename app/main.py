import asyncio

from services.chat_service import chat_loop


async def main():
    await chat_loop()

if __name__ == "__main__":
    asyncio.run(main())