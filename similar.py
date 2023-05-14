from base_genogram_func import word_numerical_value, mirrored_img, complementary_img, \
    middle_of_secret_img, get_pemutations

"""В этом файле находятся функции для поиска резонансов"""


def get_names_with_same_code(genogram_names, field, db):
    """Получение слов нужного пля БД данных по числовому коду для каждого слова геннограммы"""
    funcs = {'numerical_value': word_numerical_value,
             'mirrored_img': mirrored_img,
             'complementary_img': complementary_img,
             'middle_of_secret_img': middle_of_secret_img}
    alias = {'numerical_value': 'УВ',
             'mirrored_img': 'ЗЧО',
             'complementary_img': 'КЧО',
             'middle_of_secret_img': 'СТО'}

    res = []
    for el in genogram_names:
        row = {'name': f'{el.toPlainText()} ({el.status})', 'code': funcs[field](el.toPlainText()), 'names': ''}
        names = []
        for param in funcs:
            names.extend([word + '(' + alias[param] + ')' for word in
                                      db.get_words_by_same_code(funcs[field](el.toPlainText()), param)])
        row['names'] += ', '.join(names)
        res.append(row)

    return res


def permutations_numeric_code_resonances(genogram_names, db):
    """Получение резонансов для всех перестановок удельного веса слова"""
    resonances = dict()
    for field in genogram_names:
        name = field.toPlainText()
        if name not in resonances:
            resonances[name + f' ({field.status})'] = []
            for code in get_pemutations(word_numerical_value(name)):
                res = ', '.join(db.get_words_by_same_code(code, 'numerical_value'))
                if not res:
                    res = '-'
                resonances[name + f' ({field.status})'].append({'code': code, 'names': res})
    return resonances


def same_codes_inside_genogram(genogram_names):
    """Поиск резонансов среди имен генограммы"""
    same_codes = dict()
    funcs = {'УВ': word_numerical_value, 'ЗЧО': mirrored_img, 'КЧО': complementary_img,
             'СТО': middle_of_secret_img}
    for field in genogram_names:
        for name in funcs:
            code = funcs[name](field.toPlainText())
            if code == int(code):  # отбрасываем ноли у real если он совпадает с int
                code = int(code)
            if code not in same_codes:
                same_codes[code] = []
            same_codes[code].append(', '.join([field.toPlainText(), field.status, name]))
        numeric_code = funcs['УВ'](field.toPlainText())
        mirrored_code = funcs['ЗЧО'](field.toPlainText())
        """Получение перестановок УВ"""
        for code in get_pemutations(numeric_code):
            if (code not in same_codes):
                same_codes[code] = []
            if code not in [numeric_code, mirrored_code]:
                same_codes[code].append(', '.join([field.toPlainText(), field.status, 'перестановка УВ']))
    to_delete = [code for code in same_codes.keys() if len(same_codes[code]) < 2]
    for code in to_delete:
        del same_codes[code]
    return same_codes
