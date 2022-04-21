from best_routes.database import session
from best_routes.database import database_operation_wrapper


@database_operation_wrapper
def delete_item(item) -> None:
    session.delete(item)