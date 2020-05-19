import sqlite3
from collections import OrderedDict
from abc import ABCMeta, abstractmethod

class Field:
    __metaclass__ = ABCMeta

    def __init__(self, default):
        self.default = default

    @abstractmethod
    def check(self, value):
        """ Проверка ограничений"""
        pass

    @property
    def default(self):
        """Значение по умолчанию"""
        return self._default

    @default.setter
    @abstractmethod
    def default(self, value):
        pass


class CharField(Field):
    def __init__(self, min_length=0, max_length=100, default=''):
        self.min = min_length
        self.max = max_length
        super().__init__(default)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        if self.min > len(value):
            self._default += ' ' * (self.min - len(value))
        if self.max < len(value):
            self._default = self._default[0:self.max]

    def check(self, value):
        if len(value) < self.min:
            raise ValueError('CharField value is too short')
        if len(value) > self.max:
            raise ValueError('CharField value is too long')

    def __repr__(self):
        return "text"


class IntegerField(Field):
    def __init__(self, min_value=-1000, default=0):
        self.min = min_value
        super().__init__(default)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if self.min > value:
            self._default = self.min
        else:
            self._default = value

    def check(self, value):
        if value < self.min:
            raise ValueError('IntegerField value is too small')

    def __repr__(self):
        return "integer"


FIELDS = (CharField, IntegerField, )


class SqliteDatabase:
    def __init__(self, database):
        self.db = database

    def connect(self, *args, **kwargs):
        self.con = sqlite3.connect(self.db, *args, **kwargs)

    def create_tables(self, tables: list):
        for table in tables:
            table.create_table()

    def close(self):
        self.con.close()


class Model:
    schema = {}

    @classmethod
    def create(cls, **kwargs):
        if not cls.Meta.database:
            raise Exception("Database isn't inited")
        params = []
        for field_name, field in cls.schema[cls.__name__].items():
            kwargs.setdefault(field_name, field.default)
            field.check(kwargs[field_name])
            if isinstance(kwargs[field_name], str):
                kwargs[field_name] = f"'{kwargs[field_name]}'"
            else:
                kwargs[field_name] = str(kwargs[field_name])
            params.append(kwargs[field_name])
        request = f"INSERT INTO {cls.__name__} ({','.join(cls.schema[cls.__name__])}) VALUES ({','.join(params)})"
        cls.Meta.database.con.execute(request)

    @classmethod
    def create_table(cls):
        cls.schema.update({cls.__name__: OrderedDict()})
        params = []
        for attr in cls.__dict__:
            if isinstance(cls.__dict__[attr], FIELDS):
                params.append(f'{attr} {str(cls.__dict__[attr])}')
                cls.schema[cls.__name__].update({attr: cls.__dict__[attr]})
        if params:
            request = f"create table {cls.__name__} ({','.join(params)})"
            cls.Meta.database.con.execute(request)

    @classmethod
    def select(cls, *args) -> list:
        result = []
        if not args:
            args = ['*']
        params = ','.join([str(i) for i in args])
        request = f"SELECT {params} FROM {cls.__name__}"
        for row in cls.Meta.database.con.execute(request):
            r = ' | '.join([str(i) for i in row])
            result.append(r)
        return result

    @classmethod
    def drop(cls):
        request = f"DROP TABLE {cls.__name__}"
        cls.Meta.database.con.execute(request)