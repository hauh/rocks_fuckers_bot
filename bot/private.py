from telegram import InlineKeyboardButton as Button, InlineKeyboardMarkup
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, Filters, MessageHandler
)

from bot import with_reply, ROCKS_FUCKERS_GROUP_ID
from bot.database import Fuckers, Problems, Session, Solutions
from bot.grades import Grades

btn_new_solution = [Button("Решена!", callback_data='new_solution')]
btn_my_solutions = [Button("Мои пролазы", callback_data='my_solutions')]
btn_return = [Button("Уйти", callback_data='home')]
btn_claim = [Button("Witness me!", callback_data='claim')]
kb_labels = [[
	Button(Grades.label(grade), callback_data=f'grade_{grade.value}')
	for grade in Grades
], btn_return]


def kb_witness_solution(fucker_id, problem_number):
	key = f'{fucker_id}_{problem_number}'
	return InlineKeyboardMarkup([[
		Button("Подтверждаю", callback_data='solution_confirmed_' + key),
		Button("Пиздит", callback_data='solution_denied_' + key),
	]])


def get_fucker(user):
	session = Session()
	fucker = session.query(Fuckers).get(user.id)
	if not fucker:
		fucker = Fuckers()
		fucker.tg_id = user.id
	session.add(fucker)
	username = user.username or f'{user.first_name} {user.last_name}'.strip()
	if fucker.username != username:
		fucker.username = username
		session.commit()
	session.close()
	return fucker


@with_reply
def start(update, context):
	context.user_data.clear()
	buttons = [btn_new_solution]
	if get_fucker(update.effective_user).rating:
		buttons.append(btn_my_solutions)
	return "Решена новая проблема?", buttons


@with_reply
def new_solution(_update, context):
	context.user_data['solution'] = {}
	context.user_data['expecting_input'] = True
	return "Номер проблемы?", [btn_return]


@with_reply
def get_number(update, context):
	if not context.user_data.pop('expecting_input', False):
		return None
	try:
		if (problem_num := int(update.effective_message.text)) > Problems.MAX_NUMBER:
			raise ValueError
	except (ValueError, TypeError):
		context.user_data['expecting_input'] = True
		return "Не похоже на номер проблемы", [btn_return]
	context.user_data['solution']['number'] = problem_num
	return "Уровень сложности?", kb_labels


@with_reply
def get_grade(update, context):
	solution = context.user_data['solution']
	grade = int(update.callback_query.data.removeprefix('grade_'))
	if grade > get_fucker(update.effective_user).league + 1:
		return "Не пизди", kb_labels
	solution['grade'] = grade
	return (
		f"{Grades.label(grade)} {solution['number']} — верно?",
		[btn_claim, btn_return]
	)


@with_reply
def claim(update, context):
	fucker = get_fucker(update.effective_user)
	problem_num = context.user_data['solution']['number']
	grade = context.user_data['solution']['grade']
	confirmation_request = context.bot.send_message(
		ROCKS_FUCKERS_GROUP_ID,
		f"@{fucker.username} пролез {Grades.label(grade)} {problem_num}, видел кто?",
		reply_markup=kb_witness_solution(fucker.tg_id, problem_num)
	)
	confirmations = context.bot_data.setdefault('confirmations', {})
	confirmations[confirmation_request.message_id] = confirmation_request
	return "Ждём свидетеля", [btn_return]


@with_reply
def my_solutions(update, _context):
	solutions = Session().query(Solutions) \
		.filter(Solutions.fucker == update.effective_user.id) \
		.order_by(Solutions.ascent.desc()).all()
	return '\n'.join(
		f'{Grades.label(solution.grade)} {solution.number} {solution.ascent}'
		for solution in solutions
	), [btn_return]


private_handlers = (
	CommandHandler('start', start),
	CallbackQueryHandler(start, pattern=r'^home$'),
	CallbackQueryHandler(new_solution, pattern=r'^new_solution$'),
	MessageHandler(Filters.text, get_number),
	CallbackQueryHandler(get_grade, pattern=r'^grade_'),
	CallbackQueryHandler(claim, pattern=r'^claim$'),

	CallbackQueryHandler(my_solutions, pattern=r'^my_solutions$')
)
