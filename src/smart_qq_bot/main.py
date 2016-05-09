# -*- coding: utf-8 -*-
import argparse
import logging
import os
import socket
import sys

from smart_qq_bot.config import COOKIE_FILE
from smart_qq_bot.logger import logger
from smart_qq_bot.app import bot, plugin_manager
from smart_qq_bot.handler import MessageObserver
from smart_qq_bot.messages import mk_msg
from smart_qq_bot.excpetions import ServerResponseEmpty


def patch():
    reload(sys)
    sys.setdefaultencoding("utf-8")


def clean_cookie():
    if os.path.isfile(COOKIE_FILE):
        os.remove(COOKIE_FILE)
    logger.info("Cookie file removed.")


def main_loop(no_gui=False, new_user=False):
    patch()
    logger.setLevel(logging.INFO)
    logger.info("Initializing...")
    plugin_manager.load_plugin()
    if new_user:
        clean_cookie()
    bot.login(no_gui)
    observer = MessageObserver(bot)
    while True:
        try:
            msg_list = bot.check_msg()
            if msg_list is not None:
                observer.handle_msg_list(
                    [mk_msg(msg) for msg in msg_list]
                )
        except ServerResponseEmpty:
            continue
        except (socket.timeout, IOError):
            logger.warning("Message pooling timeout, retrying...")
        except Exception:
            logger.exception("Exception occurs when checking msg.")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-gui",
        action="store_true",
        default=False,
        help="Whether display QRCode with tk and PIL."
    )
    parser.add_argument(
        "--new-user",
        action="store_true",
        default=False,
        help="Logout old user first(by clean the cookie file.)"
    )
    args = parser.parse_args()
    main_loop(**vars(args))


if __name__ == "__main__":
    run()

