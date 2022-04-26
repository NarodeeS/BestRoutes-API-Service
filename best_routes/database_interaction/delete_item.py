from .database import db_session


def delete_item(item) -> None:
    db_session.delete(item)
    db_session.commit()
