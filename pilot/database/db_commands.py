from pilot.database.models.base import *
from typing import Dict, TypeVar


def create_entry(model: TypeVar, data: Dict, database=db_manga) -> None:

    with database.atomic():
        model.insert(data).execute()


def get_entry(model: TypeVar, name, database=db_manga):

    with database.atomic():
        response = model.get(model.name == name)

        return response

