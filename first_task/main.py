import asyncio
import aiohttp
import datetime
import os

from isdayoff import DateType, ProdCalendar
from fast_bitrix24 import BitrixAsync
from dotenv import load_dotenv
from typing import NoReturn


load_dotenv()
WEBHOOK = os.getenv("WEBHOOK", False)


class ProdCalendarWithHolidayField(ProdCalendar):
    async def _get_date_work(self, 
		data: datetime.date, 
		is_day=True, is_month=True, 
		locale=False, pre=False, sd=False, covid=False, holiday=False
	) -> str:
        return await self._get(
            '/api/getdata',
            params=self._filter_dict({
                'year': data.year,
                'month': is_month and data.month,
                'day': is_day and data.day,
                'delimeter': not (is_month and is_day) and self.DELIMETER,
                'cc': self._is_valid_locale(locale if locale else self.locale),
                'pre': int(pre),
                'sd': int(sd),
                'covid': int(covid),
                'holiday': int(holiday)
            })
        )


calendar = ProdCalendarWithHolidayField(locale='ru')


async def main() -> NoReturn:
    # Пример с 9 мая:
    # next_three_days_status: dict = {datetime.date(2022, 5, 6 + i).strftime("%Y.%m.%d"): await calendar.date(datetime.date(2022, 5, 6 + i), holiday=1) for i in range(1, 4)}

    # Текущая дата:
    next_three_days_status: dict = {}
    for i in range(1, 4):
        next_day_date: datetime = datetime.datetime.now() + datetime.timedelta(days=i)
        next_day_status: DateType = await calendar.date(next_day_date, holiday=1)
        next_three_days_status[next_day_date.strftime("%Y.%m.%d")] = next_day_status

    for day, status in next_three_days_status.items():
        if status == DateType.HOLIDAY:
            try:
                bitrix = BitrixAsync(WEBHOOK)
                task_data: dict = await bitrix.call("tasks.task.add", {"fields": {"TITLE": "task for test", "RESPONSIBLE_ID": 1}})
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
