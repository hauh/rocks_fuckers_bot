from bot.database import Fucker, Session

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
    return fucker
