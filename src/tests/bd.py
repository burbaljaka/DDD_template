import asyncio

import asyncpg


async def wait_until_responsive(host, port, timeout, pause):
    end_time = asyncio.get_event_loop().time() + timeout
    while True:
        try:
            await asyncpg.connect(user='test_user', password='test_password', database='test_db', host=host, port=port)
            return True
        except Exception as e:
            print(e)
            if asyncio.get_event_loop().time() >= end_time:
                raise TimeoutError("Database did not become responsive in time")
            await asyncio.sleep(pause)


async def wait_for_tables_to_appear(host, port, tables, timeout, pause):
    """
    Функция ожидает появления заданных таблиц в базе данных в течение указанного тайм-аута.

    :param host: хост базы данных
    :param port: порт базы данных
    :param user: имя пользователя базы данных
    :param password: пароль пользователя базы данных
    :param database: имя базы данных
    :param tables: список имен таблиц, которые необходимо проверить
    :param timeout: максимальное время ожидания в секундах
    :param pause: пауза между попытками подключения в секундах
    """
    end_time = asyncio.get_event_loop().time() + timeout
    while True:
        try:
            conn = await asyncpg.connect(user='test_user', password='test_password', database='test_db', host=host, port=port)
            # Проверяем наличие всех таблиц
            tables_exist = await check_tables_exist(conn, tables)
            await conn.close()

            if tables_exist:
                return True
            else:
                raise Exception("Not all specified tables exist in the database")
        except Exception as e:
            print(e)
            if asyncio.get_event_loop().time() >= end_time:
                raise TimeoutError("Not all tables became available in time")
            await asyncio.sleep(pause)


async def check_tables_exist(connection, tables):
    """
    Проверяет наличие заданных таблиц в базе данных.

    :param connection: соединение с базой данных
    :param tables: список имен таблиц для проверки
    :return: True, если все таблицы существуют, иначе False
    """
    for table in tables:
        query = f"SELECT to_regclass('{table}');"
        result = await connection.fetchval(query)
        if result is None:
            return False
    return True
