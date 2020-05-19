from very_simple_orm import SqliteDatabase, Model, CharField, IntegerField
import pytest


@pytest.fixture(scope="session")
def create_db():
    db = SqliteDatabase(':memory:')
    db.connect()
    yield db
    db.close()


@pytest.fixture()
def create_table(create_db):

    class BaseModel(Model):
        class Meta:
            database = create_db

    class Advert(BaseModel):
        title = CharField(max_length=20, min_length=2)
        price = IntegerField(min_value=0)

    create_db.create_tables([Advert])
    yield Advert
    Advert.drop()


def test_max_char(create_table):
    with pytest.raises(ValueError):
        create_table.create(title=' ' * 21)


def test_min_char(create_table):
    with pytest.raises(ValueError):
        create_table.create(title='')


def test_min_int(create_table):
    with pytest.raises(ValueError):
        create_table.create(price=-1)


def test_select_field(create_table):
    create_table.create(title='iPhone X', price=100)
    adverts = create_table.select('title')
    assert str(adverts[0]) == 'iPhone X'


def test_select_all(create_table):
    create_table.create(title='iPhone X', price=100)
    adverts = create_table.select()
    assert str(adverts[0]) == 'iPhone X | 100'


@pytest.mark.parametrize('default,exp', [
    (' ', '  '),
    (' '*21, ' '*20),
])
def test_default_char(default, exp):
        title = CharField(max_length=20, min_length=2, default=default)
        assert title.default == exp


def test_default_integer():
        price = IntegerField(min_value=2)
        assert price.default == 2


def test_several_tables(create_db):
    class BaseModel(Model):
        class Meta:
            database = create_db

    class Customer(BaseModel):
        name = CharField(max_length=30)
        cash = IntegerField(min_value=0)
        age = IntegerField(min_value=0)

    class Item(BaseModel):
        price = IntegerField(min_value=0)
        name = CharField(max_length=30)
        amount = IntegerField(min_value=0)

    create_db.create_tables([Customer, Item])

    Customer.create(name='Fedor', cash=100000000, age=18)
    Item.create(price=100, name='Apple', amount=98)
    Item.create(price=76, name='Orange', amount=1)
    customers = Customer.select()
    items = Item.select()
    assert str(customers[0]) == 'Fedor | 100000000 | 18'
    assert str(items[0]) == '100 | Apple | 98'
    assert str(items[1]) == '76 | Orange | 1'




