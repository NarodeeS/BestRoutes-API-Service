from best_routes.database_interaction.models import Service
from .database import db_session


def add_service(name: str, url: str, developer_id: int) -> Service:
    new_service = Service(name=name, url=url, developer_id=developer_id, is_active=True)
    db_session.add(new_service)
    db_session.commit()
    return new_service


def delete_service(service_id: int) -> None:
    service = db_session.query(Service).filter(Service.id == service_id).first()
    if service is not None:
        db_session.delete(service)
        db_session.commit()


def get_all_services() -> list:
    return db_session.query(Service).all()


def activate_service(service_id: int) -> None:
    service = db_session.query(Service).filter(Service.id == service_id).first()
    service.is_active = True
    db_session.commit()


def deactivate_service(service_id: int) -> None:
    service = db_session.query(Service).filter(Service.id == service_id).first()
    service.is_active = False
    db_session.commit()
