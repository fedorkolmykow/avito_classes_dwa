from very_simple_orm import SqliteDatabase, Model, CharField, IntegerField


db = SqliteDatabase(':memory:')


class BaseModel(Model):
    class Meta:
        database = db


class Advert(BaseModel):
    title = CharField(max_length=180)
    price = IntegerField(min_value=0)


db.connect()
db.create_tables([Advert])

Advert.create(title='iPhone X', price=100)
adverts = Advert.select()
assert str(adverts[0]) == 'iPhone X | 100'