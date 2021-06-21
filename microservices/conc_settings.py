import os

CORE_NUMBER = os.environ['CORE_NUMBER']
REQUEST_COST = os.environ['REQUEST_COST']
CURRENT_YEAR = os.environ['CURRENT_YEAR']

HEADERS = os.environ['HEADERS']

WEIGHTS_ORGANIC = os.environ['WEIGHTS_ORGANIC']

WEIGHTS_DIRECT = os.environ['WEIGHTS_DIRECT']

ABSURD_STEM_BREAKPOINT = 30

STANDART_IMPORTANCE = {
    'Возраст сайта': 0.4,
    'Стемирование': 0.3,
    'Объем статей': 0.1,
    'Ссылочное': 0.2,
}

ABSURD_IMPORTANCE = {
    'Возраст сайта': 0.15,
    'Стемирование': 0.7,
    'Объем статей': 0,
    'Ссылочное': 0.15,
}