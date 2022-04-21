from .database import session
from .models import Service
from .database_operation_wrapper import database_operation_wrapper


@database_operation_wrapper
def add_service(name: str, url: str, developer_id: int) -> Service:
    new_service = Service(name=name, url=url, developer_id=developer_id, is_active=True)
    session.add(new_service)
    return new_service


@database_operation_wrapper
def delete_service(service_id: int) -> None:
    service = session.query(Service).filter(Service.id == service_id).first()
    if service is not None:
        session.delete(service)


@database_operation_wrapper
def activate_service(service_id: int) -> None:
    service = session.query(Service).filter(Service.id == service_id).first()
    service.is_active = True
