from pathlib import Path
import logging
import sys

from aiofile import async_open
from aiopath import AsyncPath


logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
async_log_file = 'frt_photo_share_asynclog.txt'
async_log_file = str(Path(sys.argv[0]).parent.absolute().joinpath('logs', async_log_file))


async def async_logging_to_file(message: str) -> None:
    """
    The async_logging_to_file function is a coroutine that takes in a message string and writes it to the async_log_file.
    It first checks if the parent directory of async_log_file exists, and if not, creates it. It then checks whether or not
    async_logging exists as a file; if so, it opens the file in append mode (a+), otherwise it opens the file in write mode (w+).
    If neither of these conditions are met, an error message is logged to stdout.

    :param message: str: Pass the message to be logged
    :return: None
    :doc-author: Trelent
    """
    apath = AsyncPath(Path(async_log_file).parent)
    await apath.mkdir(parents=True, exist_ok=True)
    if apath.exists() and apath.is_file():
        mode_file_open: str = 'a+'

    elif not apath.exists():
        mode_file_open: str = 'w+'

    else:
        logging.warning(f'Sorry, no log-file and can\'t create "{async_log_file}".')
        return None

    async with async_open(async_log_file, mode_file_open) as afp:
        await afp.write(f'{message}\n')