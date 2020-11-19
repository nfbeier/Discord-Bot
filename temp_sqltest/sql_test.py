import numpy as np
import os
import asyncpg
import asyncio

async def run():

    credentials = {"user": 'testuser', "password": 'password', "database": 'test', "host": '127.0.0.1'}
    db = await asyncpg.create_pool(**credentials)
    await db.execute("DROP TABLE IF EXISTS users;")
    await db.execute("DROP TABLE IF EXISTS users2;")
    await db.execute("CREATE TABLE IF NOT EXISTS users(id SERIAL, discord_id bigint DEFAULT NULL, name text DEFAULT NULL, PRIMARY KEY (id));")
    await db.execute("CREATE TABLE IF NOT EXISTS users2(id SERIAL, discord_id bigint DEFAULT NULL, name text DEFAULT NULL, PRIMARY KEY (id));")
    await db.execute("INSERT INTO users(id, discord_id,name) VALUES (0, 1,'test_name');")
    await db.execute("INSERT INTO users(id, discord_id,name) VALUES (1, 5,'te');")
    await db.execute("INSERT INTO users(id, discord_id,name) VALUES (2, 7,'tt_name');")

    test = await db.fetch("SELECT discord_id from users WHERE id>=1;")
    print(test)
    for key in test:
        print(key)
    await db.close()
    
loop = asyncio.get_event_loop()
loop.run_until_complete(run())