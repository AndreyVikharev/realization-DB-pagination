from peewee import *
from pilot.database.models.base import *


class Manga(BaseModel):
    name = CharField(unique=True)
    description = CharField()
    link = CharField()
    cover = CharField()
    genres = CharField()
    rating = DecimalField(null=False)
    chapters = CharField()

    @staticmethod
    def print_manga_list():
        query = Manga.select()
        for row in query:
            print(row.id, row.name, row.rating)

    class Meta:
        table_name = 'Manga'
        database = db_manga

