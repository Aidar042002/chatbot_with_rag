import asyncpg

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self, dsn: str):
        self.pool = await asyncpg.create_pool(dsn)
        await self._create_table()

    async def _create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    content vector(384),
                    metadata JSONB DEFAULT '{}'
                )
            """)

    async def close(self):
        if self.pool:
            await self.pool.close()

db = Database()