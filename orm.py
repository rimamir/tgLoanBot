import random

from peewee import *
from datetime import datetime, timedelta


conn = PostgresqlDatabase('connection info')


class BaseModel(Model):
    class Meta:
        database = conn


class BorrowerDB(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name')
    cash = IntegerField(column_name='cash')
    rate = FloatField(column_name='rate')
    loan = IntegerField(column_name='loan')
    take_date = TextField(column_name='take_date')
    return_date = TextField(column_name='return_date')
    active = BooleanField(column_name='active')

    class Meta:
        table_name = 'borrowers'


cursor = conn.cursor()


def get_recent_borrowers():
    cur_query = BorrowerDB.select().limit(5).where(BorrowerDB.active).order_by(BorrowerDB.id.desc())
    return cur_query.dicts().execute()


def get_today_borrowers():
    today = datetime.now().date()
    cur_query = BorrowerDB.select().where((BorrowerDB.return_date == today) & BorrowerDB.active)
    return cur_query.dicts().execute()


def get_all_borrowers():
    cur_query = BorrowerDB.select().where(BorrowerDB.active)
    return cur_query.dicts().execute()


def get_weekly_borrowers():
    today = datetime.now().date()
    weekday = today.isoweekday()

    start_week = today - timedelta(days=weekday)
    end_week = today + timedelta(days=7 - weekday)
    cur_query = BorrowerDB.select().where(
        (start_week < BorrowerDB.return_date) & (BorrowerDB.return_date <= end_week) & BorrowerDB.active)
    return cur_query.dicts().execute()


def exist_active(bor_id: int):
    count = BorrowerDB.select().where((BorrowerDB.id == bor_id) & BorrowerDB.active).count()
    if count:
        return True
    return False


def change_status(bor_id: int):
    if exist_active(bor_id):
        BorrowerDB.update(active=0).where(BorrowerDB.id == bor_id).execute()
        return True

    return False


conn.close()
