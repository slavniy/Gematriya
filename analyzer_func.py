import os
from jinja2 import Template
TEMP_DIRECTORY = 'temp'

VOWELS = ['а', 'о', 'э', 'ы', 'и', 'у']

def create_report(template_name, **kwargs):
    TEMP_DIRECTORY = 'temp'
    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)
    with open(f'templates/{template_name}', encoding='utf-8') as file_:
        template = Template(file_.read())
    html = template.render(**kwargs)
    path = os.path.join(TEMP_DIRECTORY, 'report.html')
    analysis_file = open(path, mode='w', encoding='utf-8')
    print(html, file=analysis_file)
    analysis_file.close()
    return path


def get_frequency(text):
    """Частота появления букв в тексте"""
    frequency = {}
    for letter in text.lower():
        if letter not in frequency:
            frequency[letter] = 0
        frequency[letter] += 1
    len_text = len(text)
    ordered_letters = sorted(frequency.keys(), key=lambda c_letter: -frequency[c_letter])
    return [{'letter': letter, 'count': frequency[letter],
             'percentage': str(round(frequency[letter] / len_text * 100, 2))} for letter in
            ordered_letters]


def can_create_name_by_text(name, text):
    """Проверка на возможность составления слова из текста"""
    text = text.lower()
    name = name.lower()
    for letter in set(name):
        if name.count(letter) > text.count(letter):
            return False
    return True


def percentage_of_vowels_in_first_pos(words):
    """Подсчет процента открытых глассных на первой позиции"""
    return round(sum([1 for word in words if word[0].lower() in VOWELS]) / len(words) * 100, 2)


def get_names_created_by_text(text, db):
    """Получить все слва из БД, которые можно составить из текста"""
    filtered_names = []
    for table_name in db.selected_tables:
        names = [row[1] for row in db.get_names_from_table(table_name)]
        for name in names:
            if can_create_name_by_text(name, text):
                filtered_names.append(name.title())
    return filtered_names
