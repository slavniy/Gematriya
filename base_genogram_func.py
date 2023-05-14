"""В этом файле хранятся функции необходимые для построения деревьев. В модуле нет работы с БД"""
from itertools import permutations

import e_f_fl_calculate

CHARACTER_WEIGHTS = {'А': 1, 'Б': 0, 'В': 2, 'Г': 3, 'Д': 4, 'е': 5, 'з': 7, 'ё': 5, 'Е': 0, 'Ж': 0,
                     'S': 6, 'Z': 7, 'И': 8, 'Й': 0, 'i': 10, 'Ї': 0, 'ћ': 0, 'К': 20, 'Л': 30,
                     'М': 40, 'Н': 50, 'О': 70, 'П': 80, 'Р': 100, 'С': 200, 'Т': 300, 'У': 400,
                     'Ɣ': 0, 'Ф': 500, 'Х': 600, 'Ѿ': 800, 'Ц': 900, 'Ч': 90, 'Ш': 0, 'Щ': 0,
                     'Ъ': 0, 'Ы': 0, 'ь': 0, 'Ҍ': 0, 'Ю': 0, 'Я': 0, 'Э': 0, 'Ѡ': 0, 'Ѧ': 0, 'Ѫ': 0,
                     'Ѩ': 0, 'Ѭ': 0, 'Ѯ': 60, 'Ѱ': 700, 'Ө': 9, 'Ѵ': 0, 'Ӕ': 0}


def get_pemutations(number):
    """Получаем все перестановки для данного числа"""
    variants = set()
    str_number = str(number)
    for num in permutations(str_number, len(str_number)):
        variants.add(int(''.join(num)))
    return list(variants)


def check_word(func):
    """Функция-обертка, которая вернет пустую строку, если слово не было передано"""

    def wrapper_check_word(*args):
        if args[0]:
            return func(*args)
        else:
            return "-"

    return wrapper_check_word


@check_word
def word_numerical_value(word):
    """Числовой код для слова УВ"""
    numerical_value = 0
    for letter in word:
        if letter in CHARACTER_WEIGHTS:
            numerical_value += CHARACTER_WEIGHTS[letter]
        elif letter.upper() in CHARACTER_WEIGHTS:
            numerical_value += CHARACTER_WEIGHTS[letter.upper()]
        elif letter.lower() in CHARACTER_WEIGHTS:
            numerical_value += CHARACTER_WEIGHTS[letter.lower()]
    return numerical_value


def secret_image(numeric_code):
    """Тайный образ по числвому коду слова"""
    numbers = []
    res = ''
    if numeric_code < 0:
        return '-'
    while numeric_code > 0:
        numbers = [numeric_code % 1000] + numbers
        numeric_code //= 1000
    for numeric_code in numbers:
        hundreds = (numeric_code // 100) * 100
        ten = ((numeric_code // 10) % 10) * 10
        one = numeric_code % 10
        if ten == 10:
            ten, one = one, ten
        sub_res = ''
        for rank in [hundreds, ten, one]:
            if rank != 0:
                for letter in CHARACTER_WEIGHTS:
                    if CHARACTER_WEIGHTS[letter] == rank:
                        if letter != 'е':
                            letter = letter.upper()
                        sub_res += letter
                        break
        res += sub_res
    return res


@check_word
def get_letter(word, index):
    """Буква на позиции (с циклическим сдвигом)"""
    if index > 0:
        letter = word[(index - 1) % len(word)]
    elif index == -1:
        letter = word[-1].upper()
    if letter not in ['е', 'ё']:
        letter = letter.upper()
    return letter


@check_word
def get_axial_letter(word):
    """Осевые буквы слова"""
    a, b = 0, len(word) - 1
    while a < b:
        a, b = a + 1, b - 1
    return word[b:a + 1]


@check_word
def god(word):
    """Бог имени"""
    code = word_numerical_value(word) - 73
    if code > 0:
        sec_img = secret_image(code)
        return f'{sec_img} ({code})'
    else:
        return '-'


@check_word
def mirrored_img(word):
    """Зеркальный числовой образ имени"""
    return int(str(word_numerical_value(word))[::-1])


@check_word
def letter_avg_num_value(word):
    """Средний удельный вес (СУВ) буквы имени."""
    return f'{round(word_numerical_value(word) / len(word), 2)}, {word}'


@check_word
def middle_of_secret_img(word):
    """Сердце тайного образа"""
    code = word_numerical_value(word)
    variants = get_pemutations(code)
    return sum(variants) / len(variants)

def middle_of_secret_img_by_code(code):
    variants = get_pemutations(code)
    return sum(variants) / len(variants)

@check_word
def hermetic_root(word):
    """Герметический корень"""
    return word_numerical_value(word) % 9


@check_word
def complementary_img(word):
    """Комплементарный числовой образ"""
    num_value = word_numerical_value(word)
    return int(''.join([str(9 - int(num)) for num in str(num_value)]))


@check_word
def face(word):
    """Земной лик"""
    groups = {}
    level = 0
    previous = word_numerical_value(word[0])
    groups[level] = [previous]
    for letter in word[1:]:
        letter_value = word_numerical_value(letter)
        if letter_value <= previous or letter_value == 0:
            level += 1
        if level not in groups:
            groups[level] = []
        groups[level].append(letter_value)
        previous = letter_value
    total = 0
    for level in groups:
        total += sum(groups[level]) * 10 ** (3 * level)
    return f'{total} ({max(groups.keys())})'


@check_word
def get_faces(word):
    """Небесный и земной лики"""
    heavenly_face = face(word[::-1])
    earthly_face = face(word)
    if int(heavenly_face[:-4]) > int(earthly_face[:-4]):
        return f'<span style="color: red;">{heavenly_face}<br>{earthly_face}</span>'
    return f'{heavenly_face}<br>{earthly_face}'


"""Оформление значений для построения деревьев"""


@check_word
def value_and_secret_img(name, func):
    """Функция-обертка для вывода кода и его ТО"""
    code = func(name)
    return f'{code} <span class="blue">{secret_image(code)}</span>'


def e_due(energy):
    """Оформление энергетического уровня"""
    color = 'black'
    if energy > 0:
        color = 'red'
        return '<span style="color:red;">' + '+' + str(energy) + '</span>'
    if energy < 0:
        return '<span style="color:blue;' + color + '">' + str(energy) + '</span>'


@check_word
def base_letters_with_order(name):
    """Опорные букввы"""
    base_letters = dict()
    letters, power = e_f_fl_calculate.f_base_letter(name)
    for letter in letters.split(','):
        orders = []
        for i in range(len(name)):
            if name[i].lower() == letter.lower():
                orders.append(str(i + 1))
        base_letters[letter] = ', '.join(orders)
    return '; '.join(
        [f'{letter.upper()}<sub>{base_letters[letter]}</sub>' for letter in base_letters])


