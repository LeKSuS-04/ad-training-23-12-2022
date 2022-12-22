#!/usr/bin/env python3
import asyncio
import logging

from asyncio import StreamReader, StreamWriter
from pathlib import Path
from storage import FileSystemStorage
from handler import ChristmojiHandler


log = logging.getLogger(__name__)
storage = FileSystemStorage(Path.cwd() / 'data')


async def handle_client(reader: StreamReader, writer: StreamWriter):
    handler = ChristmojiHandler(reader, writer, storage)
    await handler.loop()


def handle_exception(_, context):
    msg = context.get("exception", context["message"])
    log.error(msg)
    return


async def init():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(handle_exception)

    server = await asyncio.start_server(handle_client, '0.0.0.0', 1337)

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(init())
