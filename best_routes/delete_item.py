from best_routes import db


def delete_item(item) -> None:
    db.session.delete(item)
    db.session.commit()
