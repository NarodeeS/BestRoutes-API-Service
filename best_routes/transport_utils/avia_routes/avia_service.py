from enum import Enum


def get_all_services() -> list:
    return [AviaService.TUTU,
            AviaService.KUPIBILET]


class AviaService(Enum):
    TUTU = 1
    KUPIBILET = 2
