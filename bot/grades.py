from enum import Enum


class Grades(Enum):
	"""Rock color."""

	white = 1
	yellow = 2
	green = 3
	blue = 4
	red = 5
	black = 6

	@staticmethod
	def label(value):
		return labels[Grades(value)] if isinstance(value, int) else labels[value]


labels = {
	Grades.white: '⬜',
	Grades.yellow: '🟨',
	Grades.green: '🟩',
	Grades.blue: '🟦',
	Grades.red: '🟥',
	Grades.black: '⬛'
}
