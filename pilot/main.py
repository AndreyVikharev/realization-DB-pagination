from site_parser import script
from pilot.database.db_commands import *
from pilot.database.models.manga import Manga


script.check_table(path_db)

"""Поиск в базе"""
# a = Manga.select().where(Manga.name.contains('Ва') | Manga.name.contains('ва'))
# for i in a:
#     print(i.name)

# a = Manga.get_or_none(Manga.name.contains('Ва') | Manga.name.contains('ва'))
# print(a.chapters)


