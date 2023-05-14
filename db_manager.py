from PyQt5.QtWidgets import QWidget, QCheckBox, QFileDialog, QInputDialog

import csv
import sqlite3
from base_genogram_func import word_numerical_value, mirrored_img, complementary_img, \
    middle_of_secret_img, middle_of_secret_img_by_code
from db_manager_form import DB_Form


def translit(text):
    text = '-'.join(text.lower().split())
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ja'}

    for key in slovar:
        text = text.replace(key, slovar[key])
    return text


class DbManager:
    """Класс для работы с базой данных"""

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.selected_tables = self.get_table_names()

    def delete_table(self, table_name):
        """Удаляем таблицу из БД"""
        self.cur.execute(f'DROP TABLE IF EXISTS {table_name}')
        self.conn.commit()

    def create_table(self, table_name):
        """Создаем новую таблицу с заданым именем (УВ, ЗЧО, КЧО, СТО)"""
        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           word TEXT, 
           numerical_value INTEGER, 
           mirrored_img INTEGER,
           complementary_img INTEGER,
           middle_of_secret_img INTEGER);
        """)
        self.conn.commit()

    def upload_data(self, table_name, txt_file):
        """Загружаем данные из txt"""
        self.create_table(table_name)
        file = open(txt_file, encoding='utf8')
        data = [(name, word_numerical_value(name), mirrored_img(name), complementary_img(name),
                 middle_of_secret_img(name)) for name in file.read().split()]
        self.cur.executemany(
            f'INSERT INTO {table_name} (word, numerical_value, mirrored_img, complementary_img, middle_of_secret_img) VALUES (?,?,?,?,?);',
            data)
        self.conn.commit()

    def rtl_isolate(self, line):
        return line
        return u'\u202b' + line + u'\u202c'


    def upload_csv_data(self, table_name, file):
        """Загружаем данные из txt"""
        data = []
        with open(file, encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            for row in reader:
                r1, r2, r3 = row
                if r1.isdigit():
                    code = r1
                    name = self.rtl_isolate(r2) + '/' + self.rtl_isolate(r3)
                if r2.isdigit():
                    code = r2
                    name = self.rtl_isolate(r1) + '/' + self.rtl_isolate(r3)
                if r3.isdigit():
                    code = r3
                    name = self.rtl_isolate(r1) + '/' + self.rtl_isolate(r2)
                mirrored = int(str(code)[::-1])
                complementary = int(''.join([str(9 - int(num)) for num in str(code)]))
                middle = middle_of_secret_img_by_code(code)
                data.append((f'{name}', code, mirrored, complementary, middle))
        self.create_table(table_name)
        self.cur.executemany(
            f'INSERT INTO {table_name} (word, numerical_value, mirrored_img, complementary_img, middle_of_secret_img) VALUES (?,?,?,?,?);',
            data)
        self.conn.commit()

    def get_table_names(self):
        """Получаем имена всех таблиц базы данных"""
        return [tbl[0] for tbl in
                list(self.conn.execute(f"SELECT name FROM sqlite_master  WHERE type='table';")) if
                tbl[0] != 'sqlite_sequence']

    def set_selected_tables(self, tables):
        """Выбираем активные таблицы"""
        self.selected_tables = tables

    def get_names_from_table(self, table_name):
        """Получаем все слова из таблицы"""
        return self.cur.execute(f'SELECT * FROM {table_name}').fetchall()

    def get_words_by_same_code(self, current_code, field):
        """Получаем все слова из активных таблиц по коду и полю"""
        words = []
        for table in self.selected_tables:
            rows = self.cur.execute(f'SELECT word FROM {table} WHERE {field} = ?',
                                    (current_code,)).fetchall()
            words += [row[0].title() for row in rows]
        return words

    def get_words_from_selected_tables(self):
        """Получаем все слова из активных таблиц"""
        words = []
        for table in self.selected_tables:
            rows = self.cur.execute(f'SELECT word FROM {table}').fetchall()
            words += [row[0].capitalize() for row in rows]
        return words


class DbManagerWindow(QWidget, DB_Form):
    """Класс виджета для работы с базой данных"""

    def __init__(self, main_wnd):
        super().__init__()
        self.main_wnd = main_wnd
        self.db = self.main_wnd.db
        self.setupUi(self)
        self.checkbox_tables = []
        self.update_view()
        self.use_table_btn.clicked.connect(self.use_tables)
        self.delete_table_btn.clicked.connect(self.delete_tables)
        self.create_table_btn.clicked.connect(self.create_new_table)


    def update_view(self):
        """Обновить окно виджета БД"""
        for el in self.checkbox_tables:
            el.destroy()
        self.checkbox_tables = []
        x = 20
        y = 50
        tables = self.db.get_table_names()
        for i in range(len(tables)):
            self.checkbox_tables.append(QCheckBox(self))
            self.checkbox_tables[i].setText(tables[i])
            if tables[i] in self.db.selected_tables:
                self.checkbox_tables[i].setChecked(True)
            self.checkbox_tables[i].move(x, y)
            self.checkbox_tables[i].repaint()
            self.checkbox_tables[i].update()
            y += 25


    def get_selected_tables(self):
        """Получить выбранные таблицы"""
        tables = []
        for i in range(len(self.checkbox_tables)):
            if self.checkbox_tables[i].isChecked():
                tables.append(self.checkbox_tables[i].text())
        return tables

    def use_tables(self):
        """Использовать выбранные таблицы"""
        self.db.selected_tables = self.get_selected_tables()

    def delete_tables(self):
        """Удалить таблицы"""
        tables = self.get_selected_tables()
        for table in tables:
            self.db.delete_table(table)
        self.main_wnd.refresh_db()


    def create_new_table(self):
        """Создать таблицу из файла"""
        mask = "Файлы (*.txt *.csv)"
        filename = QFileDialog.getOpenFileName(self, 'Выбрать файл txt, CSV', '', mask)[0]
        curent_name = '-'.join(filename.replace('\\', '/').split('/')[-1].split('.')[:-1])
        text, ok = QInputDialog.getText(self, 'Новая таблица',
                                        'Введите название:', text=translit(curent_name))
        if filename and ok:
            table_name = str(text)
            if filename.split('.')[-1] == 'txt':
                self.db.upload_data(table_name, filename)
            else:
                self.db.upload_csv_data(table_name, filename)
        self.main_wnd.refresh_db()
