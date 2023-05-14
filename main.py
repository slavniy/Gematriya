import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPalette, QImage, QBrush
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QLineEdit, QTextEdit, QMenu

import e_f_fl_calculate
import json
import webbrowser
from analyzer import Ui_MainWindow
from analyzer_func import *
from base_genogram_func import secret_image
from calculator import CalcWindow
from db_manager import DbManager, DbManagerWindow
from similar import *
from text_analysis import TextAnalysisWindow
from tree_generator_window import TreeGeneratorOptionsWindow, create_report
from kristal import NameKristal


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def get_qlineedits(el):
    """Рекурсивый обход элементов формы в поисках QLineEdit"""
    if isinstance(el, QLineEdit) or isinstance(el, QTextEdit):
        return [el]
    res = []
    for child in el.children():
        res += get_qlineedits(child)
    return res


def precise_division(num1, num2, precision=48):
    '''Деление двух чисел с заданной точнотью. По умолчанию 48 знаков
    Используется для расчета числа ПИ'''
    res = str(num1 // num2) + '.'
    num1 = num1 % num2
    count = 0
    while (num1 > 0) and (count < precision):
        num1 *= 10
        res += str(num1 // num2)
        num1 = num1 % num2
        count += 1
    return res


def paint_letter(word, index):
    if index is not None:
        return '<center>' + word[:index] + f'<span style="color:red;">{word[index]}</span>' + word[
                                                                                              index + 1:] + '</center>'
    else:
        return '<center>' + word + '</center>'


class Window(QMainWindow, Ui_MainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        TEMP_DIRECTORY = 'temp'
        if not os.path.exists(TEMP_DIRECTORY):
            os.makedirs(TEMP_DIRECTORY)
        self.setGeometry(100, 100, self.window().width(), 600)
        # Базы данных
        self.action_open_db_meneger.triggered.connect(self.show_db_manager_form)
        self.db = DbManager('db/words.db')
        # формы
        self.text_analysis_form = TextAnalysisWindow(self)
        self.db_manager_form = DbManagerWindow(self)
        self.tree_generator_form = TreeGeneratorOptionsWindow(self)
        self.calculator = CalcWindow()
        # обработка нажатия пунктов меню
        # генограммы
        self.action_load_genogram.triggered.connect(self.load_genogram)
        self.action_save_genogram.triggered.connect(self.save_genogram)
        self.action_clear_form.triggered.connect(self.clear_form)
        self.action_analysis.triggered.connect(self.genogram_analysis)
        self.action_letters.triggered.connect(self.tree_generator_form.show)
        self.action_find_similar.triggered.connect(self.find_similar)
        self.action_find_gen_similar.triggered.connect(self.find_gen_similar)
        self.action_E_F_FL_2.triggered.connect(self.calculator.show)
        self.action_F_FL.triggered.connect(self.create_table)
        # Расчет числа ПИ
        self.action_calculate_pi.triggered.connect(self.calculate_pi)
        # Инструементы
        self.action_open_analizator.triggered.connect(self.text_analysis_form.show)
        # Установка начальных размеров полнй в автоматическом режиме
        self.names_fields = get_qlineedits(self)
        self.status = {'subject_name': 'С', 'spouse': 'СС', 'O': 'О', 'M': 'М', 'OO': 'ОО',
                       'MO': 'МО', 'OM': 'ОМ', 'MM': 'ММ', 'OOO': 'ООО', 'MOO': 'МОО', 'OMO': 'ОМО',
                       'MMO': 'ММО', 'OOM': 'ООМ', 'MOM': 'МОМ', 'OMM': 'ОММ',
                       'MMM': 'МММ', 'subject_surname': 'С_Ф'}
        order = list(self.status.keys())
        self.ordered_fields = sorted(self.names_fields, key=lambda f: order.index(f.objectName()))
        for i in range(len(self.names_fields)):
            self.names_fields[i].setMaximumWidth(300)
            self.names_fields[i].status = self.status[self.names_fields[i].objectName()]
            self.names_fields[i].shock_letter = None
            self.names_fields[i].setFixedHeight(40)
            self.names_fields[i].setAlignment(Qt.AlignCenter)
            # создание контекстного меню
            self.names_fields[i].setContextMenuPolicy(Qt.CustomContextMenu)
            self.names_fields[i].customContextMenuRequested.connect(self.contextMenuEvent)
            self.names_fields[i].installEventFilter(self)
            self.names_fields[i].setTabChangesFocus(True)



    def eventFilter(self, obj, event):
        if (event.type() == QEvent.KeyPress) and (obj in self.names_fields):
            if event.key() == Qt.Key_Return:
                self.focusWidget().focusNextChild()
                return True
            elif event.key() == Qt.Key_Tab:
                return False
            else:
                self.focusWidget().shock_letter = None
                self.focusWidget().setAlignment(Qt.AlignCenter)
        return False





    def contextMenuEvent(self, event):
        name = self.focusWidget().toPlainText()
        contextMenu = QMenu(self.focusWidget())
        letters = []
        for i in range(len(name)):
            letters.append(contextMenu.addAction(name[i]))
        name_kristal = contextMenu.addAction('Кристалл имени')
        action = contextMenu.exec_(self.focusWidget().mapToGlobal(event))
        for i in range(len(letters)):
            if letters[i] == action:
                self.sender().setText(paint_letter(name, i))
                self.sender().shock_letter = i
        if action == name_kristal:
            name = ''.join([letter.upper() if letter not in 'её' else letter for letter in name])
            self.create_name_kristal_report(name)



    def resizeEvent(self, event):
        """Адаптация картинки с деревом при ресайзе окна"""
        image = QImage("fon.png")
        sized_image = image.scaled(self.window().width(), self.window().height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sized_image))
        self.setPalette(palette)

    def show_db_manager_form(self):
        """Открытие окна управления базами данных"""
        self.db_manager_form = DbManagerWindow(self)
        self.db_manager_form.show()

    def load_genogram(self):
        """Загрузка генограммы из файла"""
        try:
            mask = "JSON (*.json)"
            f_name = QFileDialog.getOpenFileName(self, 'Выбрать генограмму (JSON)', '', mask)[0]
            with open(f_name, 'r') as read_file:
                data = json.load(read_file)
            for q_edit in get_qlineedits(self):
                q_edit.shock_letter = data[q_edit.objectName()]["shock_letter"]
                q_edit.setText(paint_letter(data[q_edit.objectName()]["text"], q_edit.shock_letter))
                q_edit.setAlignment(Qt.AlignCenter)

        except Exception:
            pass

    def save_genogram(self):
        """сохранение генограммы в файл"""
        try:
            mask = "JSON (*.json)"
            f_name = QFileDialog.getSaveFileName(self, 'Выбрать JSON', '', mask)[0]
            data = dict()
            for q_edit in get_qlineedits(self):
                data[q_edit.objectName()] = {"text": q_edit.toPlainText(),
                                             "shock_letter": q_edit.shock_letter}
            with open(f_name, "w") as write_file:
                json.dump(data, write_file)
        except Exception:
            pass

    def clear_form(self):
        '''Очистка форм генограммы'''
        for q_edit in get_qlineedits(self):
            q_edit.setText('')
            q_edit.setAlignment(Qt.AlignCenter)

    def genogram_analysis(self):
        """Анализ генограмм"""
        # Получение имен из полей не считая фамилию
        genogram_fields = [self.names_fields[i] for i in
                           range(len(self.names_fields) - 1, -1, -1) if
                           self.names_fields[i].toPlainText() and
                           self.names_fields[i].status not in ['СС', 'С_Ф']]
        genogram_names = [field.toPlainText() for field in genogram_fields]
        text = ''.join(genogram_names)
        # Расчет процента открытых глассных на первых озициях
        percentage_of_open_vowels = percentage_of_vowels_in_first_pos(genogram_names)
        # Статистика по буква (частота встречания в именнах генограмм)
        letter_statistics = get_frequency(text)
        # Поиск резонансов по удельному весу
        names_for_genogramm_by_numerical_code = get_names_with_same_code(
            genogram_fields, 'numerical_value', self.db)
        # Получение слов, которые можно составить из букв генограммы
        names_for_genogramm_by_text = get_names_created_by_text(text, self.db)
        # Формирование отчета в формате HTML
        data = {'percentage_of_open_vowels': percentage_of_open_vowels,
                'letter_statistics': letter_statistics,
                'names_for_genogramm_by_numerical_code': names_for_genogramm_by_numerical_code,
                'names_for_genogramm_by_text': names_for_genogramm_by_text}
        path = create_report('template_genogram.html', data=data)
        webbrowser.open(path)

    def find_similar(self):
        """Формирование отчета с резонансами"""
        genogram_names = [field for field in self.ordered_fields if field.toPlainText()]
        data = {
            'УВ': get_names_with_same_code(genogram_names, 'numerical_value', self.db),
            'ЗЧО': get_names_with_same_code(genogram_names, 'mirrored_img', self.db),
            'КЧО': get_names_with_same_code(genogram_names, 'complementary_img', self.db),
            'СТО': get_names_with_same_code(genogram_names, 'middle_of_secret_img', self.db),
        }
        permutation_resonances = permutations_numeric_code_resonances(genogram_names, self.db)
        path = create_report('same_codes.html', data=data,
                             permutation_resonances=permutation_resonances)
        webbrowser.open(path)

    def find_gen_similar(self):
        """Формирование отчета с резонансами среди имён генограммы"""
        genogram_names = [field for field in self.ordered_fields if field.toPlainText()]
        data = same_codes_inside_genogram(genogram_names)
        path = create_report('same_gen_codes.html', data=data)
        webbrowser.open(path)

    def get_field_by_status(self, status):
        for field in self.names_fields:
            if field.status == status:
                return field

    def create_table(self):
        """Генерация таблицы F FL"""
        status_items = dict()
        ordered_fields = [f for f in self.ordered_fields if f.status != 'С_Ф']
        rank = len(ordered_fields)
        matrix = [[dict() for i in range(rank)] for j in range(rank)]
        labels = []
        stat = {'I': {'count': 0, 'percentage': 0},
                'II': {'count': 0, 'percentage': 0},
                'III': {'count': 0, 'percentage': 0},
                'IV': {'count': 0, 'percentage': 0},
                'V': {'count': 0, 'percentage': 0}}
        for i in range(rank):
            first = ordered_fields[i].toPlainText()
            status = ordered_fields[i].status
            status_items[status] = i
            labels.append(first + f'<sub class="status">{status}</sub>')
            for j in range(i + 1, rank):
                second = ordered_fields[j].toPlainText()
                if i != j and first and second:
                    f = e_f_fl_calculate.f(first, second)
                    fl = e_f_fl_calculate.fl(first, second)
                    if (f >= abs(fl)) and (fl > 0):
                        color = "pink"
                        stat['I']['count'] += 1
                    elif (f >= abs(fl)) and (fl < 0):
                        color = "cyan"
                        stat['II']['count'] += 1
                    elif (f < abs(fl)) and (fl > 0):
                        color = "yellow"
                        stat['III']['count'] += 1
                    elif (f < abs(fl)) and (fl < 0):
                        color = "gray"
                        stat['IV']['count'] += 1
                    else:
                        color = "white"
                        stat['V']['count'] += 1
                    if fl > 0:
                        fl = '+' + str(fl)
                    matrix[i][j] = matrix[j][i] = {'f': f, 'fl': (fl), 'color': color}

                else:
                    matrix[i][j] = matrix[j][i] = {'f': '', 'fl': '', 'color': 'white'}
        total = sum(stat[key]['count'] for key in stat)
        for key in stat:
            stat[key]['percentage'] = round(stat[key]['count'] * 100 / total, 2)

        pairs_stat = [('МММ', 'ОММ'), ('МОМ', 'ООМ'), ('ММО', 'ОМО'), ('МОО', 'ООО'), ('ММ', 'ОМ'),
                      ('МО', 'ОО'), ('М', 'О'), ('СС', 'С')]
        pairs = []
        for statuses in pairs_stat:
            f_s, m_s = statuses
            fm, ml = status_items[f_s], status_items[m_s]
            f, fl, color = matrix[fm][ml]['f'], matrix[fm][ml]['fl'], matrix[fm][ml]['color']
            pairs.append(
                {'female': labels[fm], 'f': f, 'fl': fl, 'color': color, 'male': labels[ml]})

        path = create_report('f_fl_matrix.html', matrix=matrix, labels=labels, stat=stat,
                             pairs=pairs)
        webbrowser.open(path)

    def calculate_pi(self):
        '''Формирование отчет о Расчете числа ПИ'''
        pairs_stat = [('МММ', 'ОММ'), ('МОМ', 'ООМ'), ('ММО', 'ОМО'), ('МОО', 'ООО'), ('ММ', 'ОМ'),
                      ('МО', 'ОО'), ('М', 'О'), ('СС', 'С')]
        data = []
        for pair in pairs_stat:
            female_status, male_status = pair
            female = self.get_field_by_status(female_status)
            male = self.get_field_by_status(male_status)
            f_name, m_name = female.toPlainText(), male.toPlainText()
            if f_name and m_name:
                female_code = word_numerical_value(f_name)
                male_code = word_numerical_value(m_name)
                pi = precise_division(female_code, 2 * male_code)
                pi_sec_img = secret_image(int(pi.split('.')[1]))
                base_row = ""
                for letter in pi_sec_img:
                    if letter not in base_row:
                        base_row += letter
                base_row_numeric = word_numerical_value(base_row)
                base_row_sec_img = secret_image(base_row_numeric)
                data.append({'male': f'{male.toPlainText()}({male.status})',
                             'female': f'{female.toPlainText()}({female.status})',
                             'pi': pi,
                             'pi_sec_img': pi_sec_img,
                             'base_row': base_row,
                             'base_row_numeric': base_row_numeric,
                             'base_row_sec_img': base_row_sec_img})
        path = create_report('pi_report.html', data=data)
        webbrowser.open(path)

    def create_name_kristal_report(self, name):
        '''Формирование отчет с кристалом имени'''
        drawer = NameKristal()
        drawer.draw_name_in_letter_context(name)
        drawer.draw_name_kristal(name)
        data ={'gates': drawer.get_name_gates(name),
                'portals': drawer.get_name_portals(name)
            }
        path = create_report('kristal_of_name.html', data=data)
        webbrowser.open(path)

    def refresh_db(self):
        self.db_manager_form.close()
        self.db_manager_form = DbManagerWindow(self)
        self.db_manager_form.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
