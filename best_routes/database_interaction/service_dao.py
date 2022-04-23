from best_routes.models import Service
from best_routes import db


def add_service(name: str, url: str, developer_id: int) -> Service:
    new_service = Service(name=name, url=url, developer_id=developer_id, is_active=True)
    db.session.add(new_service)
    db.session.commit()
    return new_service


def delete_service(service_id: int) -> None:
    service = Service.query.filter_by(id=service_id).first()
    if service is not None:
        db.session.delete(service)
        db.session.commit()


def get_all_services() -> list:
    return Service.query.all()


def activate_service(service_id: int) -> None:
    service = Service.query.filter_by(id=service_id).first()
    service.is_active = True
    db.session.commit()


def deactivate_service(service_id: int) -> None:
    service = Service.query.filter_by(id=service_id).first()
    service.is_active = False
    db.session.commit()
