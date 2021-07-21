"""Template Bot."""

import logging

from telegram.constants import CHAT_PRIVATE
from telegram.error import NetworkError
from telegram.ext import (
	CommandHandler, DispatcherHandlerStop, Filters, Handler, MessageHandler
)

from bot import updater, with_reply


class UpdateFilter(Handler):
	"""By default bot should be used only in private chats."""

	def __init__(self):
		super().__init__(callback=None)

	def check_update(self, update):
		if chat := update.effective_chat:
			if chat.type == CHAT_PRIVATE:
				return None
			logging.warning("Leaving %s '%s'.", chat.type, chat.title)
			chat.leave()
		raise DispatcherHandlerStop()


@with_reply
def start(_update, _context):
	"""Bot starts conversation here."""
	return "💜"


def clean(update, _context):
	"""Last handler to keep bot's message at the bottom of a chat."""
	update.effective_message.delete()


def error(update, context):
	"""Log error and restart conversation if error is from user."""
	logging.error("%s", f"{context.error.__class__.__name__}: {context.error}")
	if update and update.effective_user:
		start(update, context)


def main():
	dispatcher = updater.dispatcher
	dispatcher.add_handler(UpdateFilter())
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(MessageHandler(Filters.all, clean))
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
