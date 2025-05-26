from envparse import Env

env = Env()

DATABASE_URL = env.str(
    "DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres",
)

TEST_DATABASE_URL = env.str(
    "DATABASE_URL",
    default="postgresql+asyncpg:"
    "//test_postgres:test_postgres@0.0.0.0:5433/test_postgres",
)
