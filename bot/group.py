from datetime import date, timedelta

from telegram.error import TelegramError
from telegram.ext import CallbackQueryHandler, CommandHandler

from sqlalchemy import func

from bot.database import Fucker, Problem, Session, Solution
from bot.grades import Grades


def get_results(start_date=None):
	session = Session()
	query = session.query(
		Fucker.username, Problem.grade, func.count(Solution.id)
	).filter(
		Fucker.tg_id == Solution.fucker_id,
		Problem.id == Solution.problem_id
	).group_by(Fucker.username, Problem.grade)
	if start_date:
		query = query.filter(Solution.date_solved >= start_date)
	results = {}
	for username, grade, count in query:
		results.setdefault(username, {})[grade] = count
	formatted = []
	for username, fucker_results in results.items():
		score_row = ', '.join([
			f"{Grades.label(grade.value)}x{fucker_results[grade.value]}"
			for grade in Grades if grade.value in fucker_results
		])
		formatted.append(f"@{username}: {score_row}")
	session.commit()
	session.close()
	return '\n'.join(formatted) or "Пиздуйте лазать"


def day(update, _context):
	start = date.today() - timedelta(days=1)
	update.effective_chat.send_message(get_results(start))


def week(update, _context):
	start = date.today() - timedelta(days=7)
	update.effective_chat.send_message(get_results(start))


def month(update, _context):
	start = date.today().replace(day=1)
	update.effective_chat.send_message(get_results(start))


def total(update, _context):
	update.effective_chat.send_message(get_results())


def usage(update, _context):
	update.effective_chat.send_message(
		"Бот может по команде показывать общие результаты:\n"
		"/day — результаты за 24 часа\n"
		"/week — результаты за 7 дней\n"
		"/month — результаты за этот месяц\n"
		"/total — результаты за всё время\n\n"
		"Результаты вносятся в личном чате с ботом по команде /start."
	)


# def witnessed(update, context):
# 	_, result, solution_id = update.callback_query.data.split('_')
# 	solution_id = int(solution_id)
# 	session = Session()
# 	solution = session.query(Solution).get(solution_id)

# 	if not solution or solution.confirmed or result == 'reject':
# 		update.callback_query.answer("👎🏻 Не засчитано")
# 		if solution:
# 			session.delete(solution)
# 		try:
# 			update.effective_message.delete()
# 		except TelegramError:
# 			pass
# 		return

# 	witness_id = update.effective_user.id
# 	if witness_id == solution.fucker_id:
# 		answer = "🖕🏻 Отвали, жулик"
# 	elif witness_id == solution.witness_1_id:
# 		answer = "✌🏻 Нужен второй свидетель"
# 	elif not solution.witness_1_id:
# 		solution.witness_1_id = witness_id
# 		answer = "👍🏻 Принято"
# 	else:
# 		new_text = f"🤘🏻 {update.effective_message.text.removesuffix(', видели?')} 🤘🏻"
# 		fucker_id = solution.fucker_id
# 		try:
# 			update.effective_message.edit_text(new_text)
# 			context.bot.send_message(fucker_id, "👏🏻", disable_notification=True)
# 		except TelegramError:
# 			session.delete(solution)
# 			answer = "👎🏻 Не засчитано"
# 		else:
# 			solution.witness_2_id = witness_id
# 			answer = "👍🏻 Принято"

# 	update.callback_query.answer(answer)
# 	session.commit()
# 	session.close()


group_handlers = (
	CommandHandler('day', day),
	CommandHandler('week', week),
	CommandHandler('month', month),
	CommandHandler('total', total),
	CommandHandler('usage', usage),
	# CallbackQueryHandler(witnessed, pattern=r'^solution_(confirm|reject)_[0-9]+$')
)
