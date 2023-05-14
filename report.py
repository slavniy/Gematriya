from jinja2 import Template

import e_f_fl_calculate

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Таблица</title>
    <style>
        BODY {
            background: white; /* Цвет фона веб-страницы */
            }
        TABLE {
            border-collapse: collapse; /* Убираем двойные линии между ячейками */
            border: 2px solid white; /* Прячем рамку вокруг таблицы */
        }
        TD {
            padding: 3px; /* Поля вокруг содержимого таблицы */
            border: 1px solid maroon; /* Параметры рамки */
            text-align: center; /* Выравнивание по левому краю */
            width: 60px;
        }
         TH {
            padding: 3px; /* Поля вокруг содержимого таблицы */
            border: 1px solid maroon; /* Параметры рамки */
            text-align: center; /* Выравнивание по левому краю */
            width: 45px;
        }

      </style>

</head>
<body>


<table>

    <caption style="color: darkred"><h2>Сила материального взаимодействия F</h2></caption>
    <tr >
        <th></th>
        {% for item in name1 %}
        <th>{{item.letter}}<sub>{{item.position}}</sub><sup style="color: darkred">{{item.weight}}</sup></th>
        {% endfor %}
    </tr>

    {% for item in name2 %}
    <tr>
        <th style="text-align: left">{{item.letter}}<sub>{{item.position}}</sub><sup  style="color: darkred">{{item.weight}}</sup></th>
        {% for f in item.f %}
        <td>{{f}}</td>
        {% endfor %}
        <td>{{item.f_row_total}}</td>

    </tr>
    {% endfor %}

    <tr>
        <th></th>
        {% for f in totals.f %}
        <td>{{f}}</td>
        {% endfor %}
        <td style="color: darkred; font-weight: 900; font-size: large">{{totals.f_total}}</td>
    </tr>
</table>


<table>

    <caption style="color: darkgreen"><h2>Сила духовного взаимодействия FL</h2></caption>
    <tr >
        <th></th>
        {% for item in name1 %}
        <th>{{item.letter}}<sub>{{item.position}}</sub><sup style="color: darkorange">{{item.energy}}</sup></th>
        {% endfor %}
    </tr>

    {% for item in name2 %}
    <tr>
        <th  style="text-align: left">{{item.letter}}<sub>{{item.position}}</sub><sup  style="color: darkorange">{{item.energy}}</sup></th>
        {% for fl in item.fl %}
        <td>{{fl}}</td>
        {% endfor %}
        <td>{{item.fl_row_total}}</td>

    </tr>
    {% endfor %}

    <tr>
        <th></th>
        {% for fl in totals.fl %}
        <td>{{fl}}</td>
        {% endfor %}
        <td style="color: darkgreen; font-weight: 900; font-size: large">{{totals.fl_total}}</td>
    </tr>
</table>

</body>
</html>
"""


def report(name1: str, name2: str) -> str:

    # для вывода верхней строчки с первым именем
    a_name1 = []
    # для вывода всех строк, начинающихся с букв второго имени
    a_name2 = []

    # нижняя строчка с итогами по колонкам
    col_totals = {
        'fl': [],  # итоги по колонкам
        'fl_total': 0,  # итог по расчету
        'f': [],
        'f_total': 0
    }

    name1 = e_f_fl_calculate.lower_e(name1)
    name2 = e_f_fl_calculate.lower_e(name2)

    corrections1 = e_f_fl_calculate.calc_corrections(name1)
    corrections2 = e_f_fl_calculate.calc_corrections(name2)

    res_fl = 0
    res_f = 0

    for i, l2 in enumerate(name2):

        if l2 == 'е':
            letter = 'е'
        else:
            letter = l2.upper()

        elem = {
            'letter': letter,
            'position': i+1,
            'energy': format_plus(e_f_fl_calculate.weight(l2)),
            'weight': e_f_fl_calculate.abs_weight(l2),
            'fl': [],
            'fl_row_total': 0,
            'f': [],
            'f_row_total': 0
        }
        if l2 in corrections2:
            elem['energy'] = format_plus(corrections2[l2])

        a_name2.append(elem)

    for i, l1 in enumerate(name1):

        if l1 == 'е':
            letter = 'е'
        else:
            letter = l1.upper()

        elem = {
            'letter': letter,
            'position': i+1,
            'energy': format_plus(e_f_fl_calculate.weight(l1, corrections1)),
            'weight': e_f_fl_calculate.abs_weight(l1)
        }

        a_name1.append(elem)

        fl_total_col = 0
        f_total_col = 0
        for j, l2 in enumerate(name2):

            fl = e_f_fl_calculate.fl_(l1, l2, corrections1, corrections2)
            f = e_f_fl_calculate.f_(l1, l2)

            a_name2[j]['fl'].append(format_plus(round(fl, 4)))
            a_name2[j]['fl_row_total'] += fl

            a_name2[j]['f'].append(round(f, 4))
            a_name2[j]['f_row_total'] += f

            fl_total_col += fl
            f_total_col += f

            res_fl += fl
            res_f += f

        col_totals['fl'].append(format_plus(round(fl_total_col, 4)))
        col_totals['f'].append(round(f_total_col, 4))

    col_totals['fl_total'] = format_plus(round(res_fl, 4))
    col_totals['f_total'] = round(res_f, 4)

    for item in a_name2:
        item['fl_row_total'] = format_plus(round(item['fl_row_total'], 4))
        item['f_row_total'] = round(item['f_row_total'], 4)

    template = Template(TEMPLATE)

    return template.render(name1=a_name1, name2=a_name2, totals=col_totals)


def format_plus(number):
    if number == 0:
        return '0'
    else:
        return f'{number:+g}'
