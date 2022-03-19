from enum import Enum


def get_all_services():
    return [AviaService.TUTU,
            AviaService.KUPIBILET]


class AviaService(Enum):
    TUTU = 1
    KUPIBILET = 2
