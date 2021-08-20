from telegram import InlineKeyboardButton as Button
from telegram import InlineKeyboardMarkup
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, Filters, MessageHandler
)

from bot import ROCKS_FUCKERS_GROUP_ID, with_reply
from bot.database import Problem, Session, Solution
from bot.grades import Grades
from bot.util import get_fucker

btn_new_solution = [Button("Решена!", callback_data='new_solution')]
btn_my_solutions = [Button("Мои пролазы", callback_data='my_solutions')]
btn_return = [Button("Назад", callback_data='home')]
btn_claim = [Button("Witness me!", callback_data='claim')]
kb_labels = [[
	Button(Grades.label(grade), callback_data=f'grade_{grade.value}')
	for grade in Grades
], btn_return]


def kb_witness_solution(problem_id):
	return InlineKeyboardMarkup([[
		Button("Подтверждаю", callback_data=f'solution_confirm_{problem_id}'),
		Button("Пиздит", callback_data=f'solution_reject_{problem_id}'),
	]])


@with_reply
def start(_update, _context):
	return "Решена новая проблема?", [btn_new_solution, btn_my_solutions]


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
		if (problem_num := int(update.effective_message.text)) > Problem.MAX_NUMBER:
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
	if grade > get_fucker(update.effective_user).league + 2:
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

	session = Session()
	problem = session.query(Problem).filter(
		Problem.number == problem_num,
		Problem.grade == grade,
		Problem.active.is_(True)
	).first()
	if not problem:
		problem = Problem()
		problem.number = problem_num
		problem.grade = grade
		session.add(problem)
		session.flush()

	solution = Solution()
	solution.problem_id = problem.id
	solution.fucker_id = fucker.tg_id
	session.add(solution)
	session.commit()

	problem_str = f"{Grades.label(grade)} {problem_num}"
	context.bot.send_message(
		ROCKS_FUCKERS_GROUP_ID,
		f"@{fucker.username} fucked {problem_str}",
		disable_notification=True
	)
	session.close()
	return "Принято", [btn_return]


@with_reply
def my_solutions(update, _context):
	return '\n'.join(
		f"{Grades.label(problem_grade)} {problem_number} {date_solved}"
		for problem_grade, problem_number, date_solved in Session()
		.query(Problem.grade, Problem.number, Solution.date_solved)
		.filter(
			Solution.fucker_id == update.effective_user.id,
			Solution.problem_id == Problem.id,
		).order_by(Solution.date_solved).limit(50)
	) or "Пиздуй лазать", [btn_return]


private_handlers = (
	CommandHandler('start', start, Filters.chat_type.private),
	CallbackQueryHandler(start, pattern=r'^home$'),
	CallbackQueryHandler(new_solution, pattern=r'^new_solution$'),
	MessageHandler(Filters.chat_type.private & Filters.text, get_number),
	CallbackQueryHandler(get_grade, pattern=r'^grade_'),
	CallbackQueryHandler(claim, pattern=r'^claim$'),
	CallbackQueryHandler(my_solutions, pattern=r'^my_solutions$')
)
