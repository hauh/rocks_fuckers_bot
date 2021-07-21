"""Bot's reply logic."""

import logging

from telegram import InlineKeyboardMarkup, TelegramError


def with_reply(callback):
	"""Decorator for handlers callbacks to reply to user in a private chat.

	Decorated callback should return up to four values:

		:obj:`str`: Text to reply.
		:obj:`list`: List of lists of buttons for keyboard, default None.
		:obj:`str`: Answer for callback query, default None.
		:obj:`bool`: If answer will be shown as alert, default False.

	If nothing is returned from callback, bot won't reply anything.
	Bot will try to keep only one reply in a chat.
	"""
	def send_reply(update, context):
		result = None
		try:
			# prepare reply
			result = callback(update, context)
			if not isinstance(result, tuple):
				if not result:
					return
				result = (result,)
			text = result[0]
			buttons = InlineKeyboardMarkup(result[1]) if len(result) > 1 else None
			recent_message = context.user_data.get('_recent_message')

			# if update is from button pressed
			if update.callback_query:
				answer = result[2] if len(result) > 2 else None
				show_alert = bool(result[3]) if len(result) > 3 else False
				update.callback_query.answer(answer, show_alert)
				try:
					recent_message.edit_text(text, reply_markup=buttons)
					return
				except (AttributeError, TelegramError):
					pass

			# if update is from user input or if editing recent message failed
			context.user_data['_recent_message'] =\
				update.effective_chat.send_message(text, reply_markup=buttons)
			try:
				recent_message.delete()
			except (AttributeError, TelegramError):
				pass

		# if something went wrong log details and reraise to error handler
		except Exception:
			user = update.effective_user.username or update.effective_user.id
			logging.error("User '%s' broke bot in '%s'.", user, callback.__name__)
			if result:
				logging.error("Failed reply: %s.", result)
			raise

	return send_reply
