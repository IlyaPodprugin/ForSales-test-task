import asyncio, aiohttp
import datetime, os
import pprint

from isdayoff import DateType, ProdCalendar

from fast_bitrix24 import BitrixAsync

from dotenv import load_dotenv

from typing import NoReturn


load_dotenv()
WEBHOOK = os.getenv("WEBHOOK", False)

calendar = ProdCalendar(locale='ru')


async def main() -> NoReturn:
    """

    """
    # Пример с 9 мая:
    # next_three_days_status: dict = {datetime.date(2022, 5, 6 + i).strftime("%Y.%m.%d"): await calendar.date(datetime.date(2022, 5, 6 + i), holiday=1) for i in range(1, 4)}

    # Текущая дата:
    next_three_days_status: dict = {}
    for i in range(1, 4):
        date = datetime.datetime.now() + datetime.timedelta(days=i)
        next_three_days_status[date.strftime("%Y.%m.%d")] = await calendar.date(date, holiday=1)

    for day, status in next_three_days_status.items():
        if status == DateType.HOLIDAY:
            try:
                bitrix = BitrixAsync(WEBHOOK)
                task_data = await bitrix.call("tasks.task.add", {"fields": {"TITLE": "task for test", "RESPONSIBLE_ID": 1}})
                pprint.pprint(task_data)
            except aiohttp.client_exceptions.ClientResponseError as e:
                print("Wrong webhook url or you don't have proper rights. Contact your admin.")
            break
    else:
        print("There is no holidays in the next 3 days")

if WEBHOOK:
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
else:
    print("WEBHOOK env variable not set")
