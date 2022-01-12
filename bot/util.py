from bot.database import Fucker, Session

# Я не эксперт, но весьма вероятно, лагать он начинает из-за непротухающих сессий, которые спаунятся при каждом вводе трассы
# Что отъебнет, если поставить expire_on_commit=True ?
def get_fucker(user):
	session = Session(expire_on_commit=True)
	fucker = session.query(Fucker).get(user.id)
	if not fucker:
		fucker = Fucker()
		fucker.tg_id = user.id
	session.add(fucker)
	username = user.username or f'{user.first_name} {user.last_name}'.strip()
	if fucker.username != username:
		fucker.username = username
		session.commit()
    session.commit()
	return fucker
