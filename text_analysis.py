from PyQt5.QtWidgets import QMainWindow, QInputDialog, QFileDialog

import webbrowser
from analyzer_func import get_frequency, create_report
from analyzer_func import get_names_created_by_text
from base_genogram_func import word_numerical_value
from nltk.tokenize import sent_tokenize
from text_analysis_form import Ui_Text_analisis_form


def can_create_word_by_text(word, text):
    cur_index = 0
    for letter in word.lower():
        if letter not in text[cur_index:]:
            return False
        cur_index = text.index(letter, cur_index) + 1
    return True


class TextAnalyzer:
    """Класс содержащий функции анализа текста"""

    def __init__(self, text):
        self.text = text
        self.prepared_text = self.prepare_text()
        self.words = self.get_words()

    def prepare_text(self):
        """Удаление всех символов из текста кроме букв и пробелов"""
        new_text = ''
        for symbol in self.text.lower():
            if symbol.isalpha():
                new_text += symbol
            else:
                new_text += ' '
        return ' '.join(new_text.split())

    def get_words(self):
        """Получение списка слов из текста"""
        return self.prepared_text.split()

    def text_by_words(self, index):
        return ''.join(word[index] for word in self.words)

    def text_by_middle_letters(self):
        return ''.join(word[1:-1] for word in self.words if len(word) > 2)


    def get_letter_count_in_text(self):
        """Количество букв в тексте"""
        return sum([len(word) for word in self.words])


class TextAnalysisWindow(QMainWindow, Ui_Text_analisis_form):
    """Класс виджета анализатора текста"""

    def __init__(self, main_wnd: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_wnd = main_wnd
        self.action_load_text.triggered.connect(self.load_text)
        self.action_text_statistic.triggered.connect(self.analyze_text)
        self.action_sentence_analyzer.triggered.connect(self.split_text)
        self.action_find_words_by_name_letters.triggered.connect(self.find_words_in_text_by_name)
        self.action_first_letter_words.triggered.connect(self.words_by_text_first_letters)
        self.action_middle_letters_words.triggered.connect(self.words_by_text_middle_letters)
        self.action_last_letters_words.triggered.connect(self.words_by_text_last_letters)

    def load_text(self):
        """Загружаем текст в форму"""
        try:
            mask = "Текст (*.txt)"
            f_name = QFileDialog.getOpenFileName(self, 'Выбрать текстовый файл', '', mask)[0]
            txt_file = open(f_name, 'r', encoding='utf-8')
            text = txt_file.read()
            self.textEdit.setPlainText(text)
        except Exception:
            pass

    def split_text(self, db):
        """Разбивка текста на предложения и заполнение таблицы анализа"""
        text = self.textEdit.toPlainText()
        sentences = [sentence.strip() for sentence in sent_tokenize(text)]
        data = []
        for sentence in sentences:
            data.append({
                'text': sentence,
                'code': str(word_numerical_value(sentence)),
                'words': ', '.join(get_names_created_by_text(sentence, self.main_wnd.db))
            })

        path = create_report('template_sentence_analyze.html', data=data)
        webbrowser.open(path)

    def analyze_text(self):
        """Генерирует HTML со статистикой по тексту (кол-во букв, слов)"""
        text = self.textEdit.toPlainText()
        analyzer = TextAnalyzer(text)
        data = {'letter_count': analyzer.get_letter_count_in_text(),
                'words_count': len(analyzer.words),
                'text_numerical_value': word_numerical_value(text),
                'letter_statistics': get_frequency(''.join(analyzer.words))}
        path = create_report('template_text.html', data=data)
        webbrowser.open(path)

    def find_words_in_text_by_name(self):
        """Обработчик меню, вызывает форму для ввода имени.
        Затем ищет слова начинающиеся на буквы имени"""
        name, ok_pressed = QInputDialog.getText(self, "Имя", "Введите имя:")
        if ok_pressed and name:
            data = dict()
            data['name'] = name.upper()
            data['words'] = self.find_words_for_letters_in_name(name)
            path = create_report('template_words_for_name.html', data=data)
            webbrowser.open(path)

    def find_words_for_letters_in_name(self, name):
        """Получает имя и возвращает список слов начинающихся на буквы имени"""
        analyzer = TextAnalyzer(self.textEdit.toPlainText())
        name_letters = set(name.upper())
        res = {letter: [] for letter in name_letters}
        for word in analyzer.words:
            first_letter = word[0].upper()
            if (first_letter in name_letters) and word.capitalize() not in res[first_letter]:
                res[first_letter].append(word.capitalize())
        return res


    def words_by_text_report(self, text, title):
        words = self.main_wnd.db.get_words_from_selected_tables()
        res = ', '.join(sorted([word for word in words if can_create_word_by_text(word, text)]))
        path = create_report('template_list.html', data={'words' : res, 'title' : title})
        webbrowser.open(path)

    def words_by_text_first_letters(self):
        text = ''.join(word[0] for word in TextAnalyzer(self.textEdit.toPlainText()).words)
        self.words_by_text_report(text, 'Слова по первым буквам')

    def words_by_text_middle_letters(self):
        words_in_text = TextAnalyzer(self.textEdit.toPlainText()).words
        text = ''.join(word[1:-1] for word in words_in_text if len(word) > 2)
        self.words_by_text_report(text, 'Слова по промежуточным буквам')

    def words_by_text_last_letters(self):
        text = ''.join(word[-1] for word in TextAnalyzer(self.textEdit.toPlainText()).words)
        self.words_by_text_report(text, 'Слова по последним буквам')

