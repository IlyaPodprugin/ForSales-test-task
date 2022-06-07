# Тестовое задание ForSales (Python). Подпругин Илья

---

## Установка
```shell
git clone git@github.com:IlyaPodprugin/ForSales-test-task.git
cd ForSales-test-task
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Задание №1
В этом задании для получения информации о праздниках я использую библиотеку [isdayoff](https://pypi.org/project/isdayoff/). Для работы с Битрикс24 используется [fast_bitrix24](https://pypi.org/project/fast-bitrix24/). Так как [isdayoff](https://pypi.org/project/isdayoff/) асинхронная библиотека, то и работа с Битрикс24 осуществляется в асинхронном режиме.

Для определения не просто выходного, а именно праздничного дня, нужно добавить в запрос к API [isDayOff()](https://www.isdayoff.ru/) параметр `holiday=1`. Так как [isdayoff](https://pypi.org/project/isdayoff/) ещё не обновилась для использования данного функционала, мной было принято решение создать класс-наследник `ProdCalendarWithHolidayField` основного класса библиотеки `ProdCalendar` и переопределить метод отправления запроса.

Для полноценной работы первого задания необходимо после установки зависимостей открыть файл `isdayoff/typingapi.py` и добавить новые атрибуты в 2 класса:

```python
class ParamsApi(TypedDict):
    locale: str
    pre: bool
    sd: bool
    covid: bool
	# Новый атрибут holiday
    holiday: bool

class DateType(IntEnum):
    WORKING = 0
    NOT_WORKING = 1
    SHORTENED = 2
    WORKING_DAY = 4
	# Новый атрибут HOLIDAY
    HOLIDAY = 8
```

Также необходимо создать `.env` файл в корне репозитория и заполнить следующими переменными:

```
WEBHOOK=Ваш вебхук

SECRET_KEY=Ваш ключ
DEBUG=True
ALLOWED_HOSTS="*"
```

### Запуск
```shell
python3 first_task/main.py
```

## Задание №2
Для работы с Битрикс24 снова используется [fast_bitrix24](https://pypi.org/project/fast-bitrix24/).

Вся логика работы с Битрикс24 инкапсулирована в модуль `deal/services`.

Для экономии времени я не стал заморачиваться с созданием поля с продуктами в виде списка сущностей (объектов) товаров в Битрикс, поэтому сделал это поле строкового типа, но, разумеется, оно должно быть списком объектов.

### Запуск
```shell
python3 second_task/manage.py runserver
```

---

Мой телеграм: [@ilya_pod](https://t.me/ilya_pod)