from peewee import *


path_db = r'C:\Users\ThinkPad\PycharmProjects\python_basic_diploma\pilot\database\project_db.db'

db_manga = SqliteDatabase(path_db)


class BaseModel(Model):
    class Meta:
        database = db_manga
