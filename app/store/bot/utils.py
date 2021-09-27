from datetime import datetime, timedelta


async def to_string(date_time_obj: datetime) -> str:
    return date_time_obj.strftime("%d/%m/%y %H:%M:%S")


async def to_datetime(date_time_str: str) -> datetime:
    return datetime.strptime(date_time_str, "%d/%m/%y %H:%M:%S")


async def get_delta(datetime_obj: datetime, datetime_obj_subtrahend: datetime) -> timedelta:
    return datetime_obj - datetime_obj_subtrahend


async def int_to_datetime(period_min: int) -> timedelta:
    return timedelta(minutes=period_min)


