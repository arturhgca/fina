from peewee import SqliteDatabase, Model

db = SqliteDatabase("fina-core.db")


class BaseModel(Model):
    class Meta:
        database = db
