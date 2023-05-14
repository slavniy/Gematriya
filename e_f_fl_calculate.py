
base_dict = {
    'а': 1, 'в': -2, 'г': 3, 'д': 4, 'е': -5, 'ё': -5, 's': -6, 'з': -7, 'и': -8, 'й': 0, 'ѳ': -9,
    'i': 10, 'к': -20, 'л': -30, 'м': 40, 'н': -50, 'ѯ': 60, 'о': 70, 'п': -80, 'ч': 90,
    'р': 100, 'с': 200, 'т': 300, 'у': 400, 'ф': 500, 'х': 600, 'ѱ': -700, 'ѿ': 800, 'ц': 900
}


def weight(letter: str, extra_dict=None) -> int:
    if extra_dict is None:
        extra_dict = {}

    if letter != 'Е':
        letter = letter.lower()

    if letter in extra_dict:
        return extra_dict[letter]
    elif letter in base_dict:
        return base_dict[letter]
    else:
        return 0


def abs_weight(letter: str, extra_dict=None) -> int:
    if extra_dict is None:
        extra_dict = {}
    return abs(weight(letter, extra_dict))


def f_(l1: str, l2: str) -> float:

    w_l1 = abs_weight(l1)
    w_l2 = abs_weight(l2)

    if w_l1 == w_l2:
        return 0

    result = w_l1 * w_l2 / (w_l1 - w_l2)**2

    if result == 0:
        result = 0

    return result


def fl_(l1: str, l2: str, extra_dict1=None, extra_dict2=None) -> float:

    if extra_dict1 is None:
        extra_dict1 = {}
    if extra_dict2 is None:
        extra_dict2 = {}

    w_l1 = weight(l1, extra_dict1)
    w_l2 = weight(l2, extra_dict2)
    aw_l1 = abs_weight(l1, extra_dict1)
    aw_l2 = abs_weight(l2, extra_dict2)

    if aw_l1 == aw_l2:
        return 0

    result = (w_l1 + w_l2) / abs(aw_l1 - aw_l2)

    return result


def e(text: str) -> int:
    result = 0

    text = lower_e(text)

    corrections = calc_corrections(text, for_energy=True)

    for letter in text:
        result += weight(letter, corrections)

    return result


def m(text: str) -> int:

    result = 0
    for letter in text:
        result += abs_weight(letter)

    return result


def f_base_letter(text: str) -> (str, float):

    if len(text) < 2:
        return '', 0

    result = {}

    text = lower_e(text)

    for i, l1 in enumerate(text[:-1]):
        for l2 in text[i+1:]:
            f_meaning = f_(l1, l2)
            if l1 in result:
                result[l1] += f_meaning
            else:
                result[l1] = f_meaning
            if l2 in result:
                result[l2] += f_meaning
            else:
                result[l2] = f_meaning

    max_val = max(result.values())
    letters = [k for k, v in result.items() if v == max_val]

    return upper_e(','.join(letters)), round(max_val, 4)


def lower_e(text: str) -> str:

    result = ''
    for letter in text:
        if letter == 'Е' or letter == 'E':
            letter_l = 'Е'
        else:
            letter_l = letter.lower()
        result += letter_l

    return result


def upper_e(text: str) -> str:

    result = ''
    for letter in text:
        if letter == 'е' or letter == 'e':
            letter_u = 'е'
        else:
            letter_u = letter.upper()
        result += letter_u

    return result


def f(name1: str, name2: str) -> float:

    if name1 == '' or name2 == '':
        return 0

    result = 0

    for l1 in name1:
        for l2 in name2:
            result += f_(l1, l2)

    return round(result, 4)


def fl(name1: str, name2: str) -> float:

    if name1 == '' or name2 == '':
        return 0

    name1 = lower_e(name1)
    name2 = lower_e(name2)

    result = 0

    for l1 in name1:
        for l2 in name2:
            result += fl_(l1, l2, calc_corrections(name1), calc_corrections(name2))

    return round(result, 4)


def calc_corrections(name, for_energy=False):

    result = {}
    androgynous = {}

    name = lower_e(name)

    if 'б' in name and not for_energy:
        result['б'] = -2

    if 'к' not in name and 's' not in name:
        return result

    energy = 0

    for i, letter in enumerate(name):
        letter = name[i]

        if letter in ('к', 's'):
            if letter in androgynous:
                androgynous[letter] += abs_weight(letter)
            else:
                androgynous[letter] = abs_weight(letter)
        else:
            energy += weight(letter)

    androgynous_list = sorted(androgynous.items(), key=lambda item: item[1], reverse=True)
    androgynous = dict(androgynous_list)

    for key in androgynous:

        if energy >= 0:
            energy -= androgynous[key]
            result[key] = -abs_weight(key)
        elif energy < 0:
            energy += androgynous[key]
            result[key] = abs_weight(key)

    return result
