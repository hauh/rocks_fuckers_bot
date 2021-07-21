"""Template Bot package."""

import logging
import os
import sys

from telegram import ParseMode
from telegram.error import InvalidToken
from telegram.ext import Defaults, Updater

from bot.reply import with_reply

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
	datefmt="%Y.%m.%d %H:%M:%S"
)

try:
	updater = Updater(
		token=os.environ['TOKEN'],
		defaults=Defaults(parse_mode=ParseMode.MARKDOWN),
	)
except KeyError:
	logging.critical("'TOKEN' environment variable is required.")
	sys.exit(1)
except InvalidToken:
	logging.critical("Invalid token.")
	sys.exit(1)
