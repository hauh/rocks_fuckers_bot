"""Template Bot."""

import logging

from telegram.constants import CHAT_PRIVATE
from telegram.error import NetworkError
from telegram.ext import (
	DispatcherHandlerStop, Filters, Handler, MessageHandler
)

from bot import ROCKS_FUCKERS_GROUP_ID, updater
from bot.group import group_handlers
from bot.private import private_handlers, start


class UpdateFilter(Handler):
	"""By default bot should be used only in private chats."""

	def __init__(self):
		super().__init__(callback=None)

	def check_update(self, update):
		if chat := update.effective_chat:
			if chat.type == CHAT_PRIVATE or chat.id == ROCKS_FUCKERS_GROUP_ID:
				return None
			logging.warning("Leaving %s '%s'.", chat.type, chat.title)
			chat.leave()
		raise DispatcherHandlerStop()


def clean(update, _context):
	"""Last handler to keep bot's message at the bottom of a chat."""
	update.effective_message.delete()


def error(update, context):
	"""Log error and restart conversation if error is from user."""
	logging.error("%s", f"{context.error.__class__.__name__}: {context.error}")
	chat = update.effective_chat
	if update and update.effective_user and chat and chat.type == CHAT_PRIVATE:
		start(update, context)


def main():
	dispatcher = updater.dispatcher
	dispatcher.add_handler(UpdateFilter())

	for handler in private_handlers:
		dispatcher.add_handler(handler)
	for handler in group_handlers:
		dispatcher.add_handler(handler)

	cleaner = MessageHandler(Filters.all & Filters.chat_type.private, clean)
	dispatcher.add_handler(cleaner, group=999)
	dispatcher.add_error_handler(error)

	try:
		updater.start_polling()
	except NetworkError:
		logging.critical("Connection failed.")
	else:
		logging.info("Bot started!")
		updater.idle()
		logging.info("Turned off.")


if __name__ == "__main__":
	main()
