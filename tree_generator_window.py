from PyQt5.QtWidgets import QWidget, QMainWindow, QCheckBox

import webbrowser
from analyzer_func import get_names_created_by_text, create_report
from base_genogram_func import *
from tree_generator_form import Ui_PosForm


def get_check_boxes(el):
    """Рекурсивый обход элементов формы в поисках QCheckBox"""
    if isinstance(el, QCheckBox):
        return [el]
    res = []
    for child in el.children():
        res += get_check_boxes(child)
    return res


class TreeGeneratorOptionsWindow(QWidget, Ui_PosForm):
    """Форма с чек-боксами для формирования деревьев"""

    def __init__(self, main_wnd: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_wnd = main_wnd
        self.trees_generate_btn.clicked.connect(self.generate_trees)

    def get_shock_letter(self, field):
        if field.toPlainText() and field.shock_letter is not None:
            return field.toPlainText()[
                       field.shock_letter].upper() + f'<sub>{field.shock_letter + 1}</sub>'
        return '-'

    def numerical_value_report(self):
        """Дополнительный отчет по дереву с удельными весами"""
        table = []
        for field in self.main_wnd.names_fields:
            if field.toPlainText():
                table.append({'name': field.toPlainText(),
                              'status': field.status,
                              'value': word_numerical_value(field.toPlainText())})
        table.sort(key=lambda row: row["value"], reverse=True)
        mother_branch = sum([el["value"] for el in table if el['status'][-1] == 'М'])
        father_branch = sum([el["value"] for el in table if el['status'][-1] == 'О'])
        female_names = sum([el["value"] for el in table if el['status'][0] == 'М'])
        male_names = sum([el["value"] for el in table if el['status'][0] == 'О'])
        return {'table': table, 'mother_branch': mother_branch,
                'father_branch': father_branch, 'female_names': female_names,
                'male_names': male_names}

    def god_report(self):
        """Дополнительный отчет по Богам имен"""
        fields = [field for field in self.main_wnd.names_fields if field.toPlainText()]
        table = []
        for f in fields:
            wnv = word_numerical_value(f.toPlainText())
            similar = self.main_wnd.db.get_words_by_same_code(wnv - 73, 'numerical_value')
            table.append({'name': f.toPlainText(), 'status': f.status, 'value': wnv,
                          'god_code': wnv - 73, 'similar': ', '.join(similar)})

        female_names = sum([el["value"] for el in table if el['status'][0] == 'М'])
        male_names = sum([el["value"] for el in table if el['status'][0] == 'О'])
        mother_code = female_names - 472
        father_code = male_names - 1343
        system_code = female_names + male_names - 73
        return {'table': table,
                'father_god': f'{secret_image(father_code)} ({father_code})',
                'mother_god': f'{secret_image(mother_code)} ({mother_code})',
                'system_god': f'{secret_image(system_code)} ({system_code})'}

    def letters_report(self, index):
        """Дополнительная информация о дереве с буквами на позиции"""
        fields = [field for field in self.main_wnd.names_fields if field.toPlainText()]
        letters = [get_letter(field.toPlainText(), index) for field in fields]
        text = ''.join(letters)
        names = get_names_created_by_text(text, self.main_wnd.db)
        if names:
            return ', '.join(names)
        else:
            return 'не обнаружены'

    def last_letters_report(self):
        """Дополнительная информация о дереве с буквами на последней позиции"""
        fields = [field for field in self.main_wnd.names_fields if field.toPlainText()]
        count = 0
        names = []
        for field in fields:
            last_letter = get_letter(field.toPlainText(), -1)
            if e_f_fl_calculate.e(last_letter) < 0:
                count += 1
                names.append(f'{field.toPlainText()}({field.status})')
        return {'negative_percentage': round(count * 100 / len(fields), 2), 'names': names}

    def base_letters_report(self):
        """Дополнительная информация о дереве с буквами на последней позиции"""
        fields = [field for field in self.main_wnd.names_fields if field.toPlainText()]
        stat = dict()
        orders = []
        for field in fields:
            name = field.toPlainText()
            letters, power = e_f_fl_calculate.f_base_letter(name)
            for letter in letters.split(','):
                if letter not in stat:
                    stat[letter] = 0
                stat[letter] += 1
                for i in range(len(name)):
                    if name[i].lower() == letter.lower():
                        orders.append(i + 1)
        total = sum(stat.values())
        pos_stat = {str(order): orders.count(order) for order in set(orders)}
        total2 = sum(pos_stat.values())
        sorted_tuples = sorted(stat.items(), key=lambda item: item[1], reverse=True)
        sorted_tuples2 = sorted(pos_stat.items(), key=lambda item: item[1], reverse=True)
        sorted_stat = {k: {'count': v, 'percentage': round(v * 100 / total, 2)} for k, v in
                       sorted_tuples}
        sorted_pos_stat = {k: {'count': v, 'percentage': round(v * 100 / total2, 2)} for k, v in
                           sorted_tuples2}
        return {'stat': sorted_stat, 'pos_stat': sorted_pos_stat}

    def shock_letters_report(self):
        """Дополнительная информация о дереве с ударными буквами"""
        fields = [field for field in self.main_wnd.names_fields if field.toPlainText()]
        letters = []
        orders = []
        for field in fields:
            if field.toPlainText() and field.shock_letter is not None:
                letters.append(field.toPlainText()[field.shock_letter].upper())
                orders.append(field.shock_letter + 1)
        base_letters = set(letters)
        letters_stat = []
        for letter in base_letters:
            count = letters.count(letter)
            percentage = count / len(letters) * 100
            letters_stat.append({'letter': letter, 'count': count, 'percentage': round(percentage, 2)})
        letters_stat.sort(key=lambda x: x['count'], reverse=True)
        base_orders = set(orders)
        orders_stat = []
        for order in base_orders:
            count = orders.count(order)
            percentage = count / len(orders) * 100
            orders_stat.append({'order': order, 'count': count, 'percentage': round(percentage, 2)})
        orders_stat.sort(key=lambda x: x['count'], reverse=True)
        return {'letters_stat': letters_stat, 'orders_stat': orders_stat}

    def get_field_by_status(self, status):
        for field in self.main_wnd.names_fields:
            if field.status == status:
                return field

    def energy_report(self):
        """Дополнительная информация о дереве с E разделом"""
        fields = [field for field in self.main_wnd.names_fields if field.toPlainText()]
        names = []
        for field in fields:
            name, status = field.toPlainText(), field.status
            row = {'name': name, 'status': status, 'e': e_f_fl_calculate.e(name)}
            names.append(row)
        return {'names': sorted(names, key=lambda x: -x['e'])}

    def energy_pairs_attributes(self):
        """Окрашивание пар муж-жена в дереве с E разделом"""
        pairs = [{'М': 'ОММ', 'Ж': 'МММ'}, {'М': 'ООМ', 'Ж': 'МОМ'}, {'М': 'ОМО', 'Ж': 'ММО'},
                 {'М': 'ООО', 'Ж': 'МОО'}, {'М': 'ОМ', 'Ж': 'ММ'}, {'М': 'ОО', 'Ж': 'МО'},
                 {'М': 'О', 'Ж': 'М'}]
        colors = dict()
        bolds = dict()
        for pair in pairs:
            man = self.get_field_by_status(pair['М'])
            woman = self.get_field_by_status(pair['Ж'])
            man_name, woman_name = man.toPlainText(), woman.toPlainText()
            if man_name and woman_name:
                man_e = e_f_fl_calculate.e(man_name)
                woman_e = e_f_fl_calculate.e(woman_name)
                if (man_e > 0) and (woman_e < 0) and (abs(man_e) > abs(woman_e)):
                    color = 'yellow'
                elif (man_e > 0) and (woman_e < 0) and (abs(man_e) < abs(woman_e)):
                    color = 'gray'
                elif (man_e < 0) and (woman_e > 0):
                    color = 'cyan'
                elif (man_e > 0) and (woman_e > 0) or (man_e < 0) and (woman_e < 0):
                    color = 'purple'
                else:
                    color = 'white'
                colors[man.status] = color
                colors[woman.status] = color
                if man_e > woman_e:
                    bolds[man.status] = 'bold'
                elif woman_e > man_e:
                    bolds[woman.status] = 'bold'
        return colors, bolds

    def generate_trees(self):
        self.gen_checkBox.tree_data = {'title': 'Генограмма',
                                       'func': lambda name: name if name else '-'}
        self.let1_checkBox.tree_data = {'title': f'Буквы на позиции {1}',
                                        'func': lambda name: get_letter(name, 1),
                                        'add_report_func': lambda: self.letters_report(1)}
        self.let2_checkBox.tree_data = {'title': f'Буквы на позиции {2}',
                                        'func': lambda name: get_letter(name, 2),
                                        'add_report_func': lambda: self.letters_report(2)}
        self.let3_checkBox.tree_data = {'title': f'Буквы на позиции {3}',
                                        'func': lambda name: get_letter(name, 3),
                                        'add_report_func': lambda: self.letters_report(3)}
        self.let4_checkBox.tree_data = {'title': f'Буквы на позиции {4}',
                                        'func': lambda name: get_letter(name, 4),
                                        'add_report_func': lambda: self.letters_report(4)}
        self.let5_checkBox.tree_data = {'title': f'Буквы на позиции {5}',
                                        'func': lambda name: get_letter(name, 5),
                                        'add_report_func': lambda: self.letters_report(5)}
        self.let6_checkBox.tree_data = {'title': f'Буквы на позиции {6}',
                                        'func': lambda name: get_letter(name, 6),
                                        'add_report_func': lambda: self.letters_report(6)}
        self.let7_checkBox.tree_data = {'title': f'Буквы на позиции {7}',
                                        'func': lambda name: get_letter(name, 7),
                                        'add_report_func': lambda: self.letters_report(7)}
        self.let8_checkBox.tree_data = {'title': f'Буквы на позиции {8}',
                                        'func': lambda name: get_letter(name, 8),
                                        'add_report_func': lambda: self.letters_report(8)}
        self.let9_checkBox.tree_data = {'title': f'Буквы на позиции {9}',
                                        'func': lambda name: get_letter(name, 9),
                                        'add_report_func': lambda: self.letters_report(9)}
        self.last_letter_checkBox.tree_data = {'title': 'Буквы на последней позиции',
                                               'func': lambda name: get_letter(name, -1)}
        self.axial_letter_checkBox.tree_data = {'title': 'Осевые буквы', 'func': get_axial_letter}
        self.spec_weight_checkBox.tree_data = {'title': 'Удельные веса',
                                               'func': lambda name:
                                               value_and_secret_img(name, word_numerical_value),
                                               'add_report_func': self.numerical_value_report}
        self.mirrored_img_checkBox.tree_data = {'title': 'Зеркальный числовой образ',
                                                'func': lambda name: value_and_secret_img(name,
                                                                                          mirrored_img)}
        self.complementary_img_checkBox.tree_data = {'title': 'Комплементарный числовой образ',
                                                     'func': lambda name: value_and_secret_img(name,
                                                                                               complementary_img)}
        self.hermetic_root_checkBox.tree_data = {'title': 'Герметический корень',
                                                 'func': lambda name: value_and_secret_img(name,
                                                                                           hermetic_root)}
        self.god_checkBox.tree_data = {'title': 'Бог имени', 'func': god,
                                       'add_report_func': self.god_report}
        self.average_weight_checkBox.tree_data = {'title': 'Cредний удельный вес буквы имени',
                                                  'func': letter_avg_num_value}
        self.middle_checkBox.tree_data = {'title': 'Сердце тайного образа',
                                          'func': lambda name: value_and_secret_img(name,
                                                                                    middle_of_secret_img)}
        self.heavenly_face_checkBox.tree_data = {'title': 'Лики', 'func': get_faces}
        self.energy_checkBox.tree_data = {'title': 'Энергетическая направленность (E)',
                                          'func': lambda name: e_due(e_f_fl_calculate.e(name)),
                                          'add_report_func': self.energy_report}
        self.base_letter_checkBox.tree_data = {'title': 'Опорные буквы и их позиции',
                                               'func': base_letters_with_order,
                                               'add_report_func': self.base_letters_report}
        self.shock_checkBox.tree_data = {'title': 'Ударные буквы'}
        trees_checkboxes = get_check_boxes(self)
        order = ['gen_checkBox', 'let1_checkBox', 'let2_checkBox', 'let3_checkBox', 'let4_checkBox',
                 'let5_checkBox', 'let6_checkBox', 'let7_checkBox', 'let8_checkBox',
                 'let9_checkBox', 'last_letter_checkBox', 'axial_letter_checkBox', 'shock_checkBox',
                 'spec_weight_checkBox', 'mirrored_img_checkBox', 'complementary_img_checkBox',
                 'hermetic_root_checkBox', 'average_weight_checkBox', 'middle_checkBox',
                 'god_checkBox', 'base_letter_checkBox', 'heavenly_face_checkBox',
                 'energy_checkBox']
        trees_checkboxes = sorted(trees_checkboxes, key=lambda x: order.index(x.objectName()))
        datas = []
        for i in range(len(trees_checkboxes)):
            if trees_checkboxes[i].isChecked():
                additional_report = None
                if 'add_report_func' in trees_checkboxes[i].tree_data:
                    additional_report = trees_checkboxes[i].tree_data['add_report_func']()
                if trees_checkboxes[i].tree_data['title'] == 'Ударные буквы':
                    data = {'title': trees_checkboxes[i].tree_data['title'],
                            'letters': [self.get_shock_letter(field) for field in
                                        self.main_wnd.names_fields],
                            'additional_report': self.shock_letters_report()}
                elif trees_checkboxes[i].tree_data['title'] != 'Энергетическая направленность (E)':
                    data = {'title': trees_checkboxes[i].tree_data['title'],
                            'letters': [trees_checkboxes[i].tree_data['func'](field.toPlainText())
                                        for
                                        field in
                                        self.main_wnd.names_fields],
                            'additional_report': additional_report}
                else:
                    colors, bolds = self.energy_pairs_attributes()
                    letters = []
                    for field in self.main_wnd.names_fields:
                        if field.status in bolds:
                            value = '<span class = "bold">' + trees_checkboxes[i].tree_data['func'](
                                field.toPlainText()) + '</span>'
                        else:
                            value = trees_checkboxes[i].tree_data['func'](field.toPlainText())
                        if field.status in colors:
                            value += f'<span class = "round {colors[field.status]}"> </span>'
                        letters.append(value)
                    data = {'title': trees_checkboxes[i].tree_data['title'],
                            'letters': letters,
                            'additional_report': additional_report}

                datas.append(data)
        path = create_report('template_letter_pos.html', datas=datas)
        webbrowser.open(path)


def get_paternal_branch(fields):
    """Получение полей отцовской ветки"""
    return [field for field in fields if field.status[-1] == "О"]


def get_mother_branch(fields):
    """Получение полей материнской ветки"""
    return [field for field in fields if field.status[-1] == "М"]


def get_male_fields(fields):
    """Получение полей с мужскими именами"""
    return [field for field in fields if field.status[0] == "О"]


def get_female_fields(fields):
    """Получение полей с женскими именами"""
    return [field for field in fields if field.status[0] == "М"]
