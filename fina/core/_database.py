from __future__ import annotations

import datetime

from peewee import SqliteDatabase, Model, DateTimeField, BooleanField

db = SqliteDatabase("fina-core.db")


class BaseModel(Model):
    created_on = DateTimeField(default=datetime.datetime.now)
    updated_on = DateTimeField(default=datetime.datetime.now)
    is_deleted = BooleanField(default=False)

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.save()

    def undelete(self) -> None:
        self.is_deleted = False
        self.save()

    class Meta:
        database = db
