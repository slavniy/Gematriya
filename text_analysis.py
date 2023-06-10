from PyQt5.QtWidgets import QMainWindow, QInputDialog, QFileDialog

import webbrowser
from analyzer_func import get_frequency, create_report
from analyzer_func import get_names_created_by_text
from base_genogram_func import word_numerical_value
from nltk.tokenize import sent_tokenize
from forms.text_analysis_form import Ui_Text_analisis_form
from e_f_fl_calculate import e
from pprint import pprint

def can_create_word_by_text(word, text):
    cur_index = 0
    for letter in word.lower():
        if letter not in text[cur_index:]:
            return False
        cur_index = text.index(letter, cur_index) + 1
    return True

def get_areas(text):
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    spechial_words = ['#Область', '#Глава', '\n\n']
    for separator in spechial_words:
        text = text.replace(separator, '<br>')
    return text.split('<br>')


def get_paragraphs(area):
    return area.split('\n')


def get_sentences(paragraf):
    separators = ['.', '!', '?']
    for separator in separators:
        paragraf = paragraf.replace(separator, separator + '<br>').strip()
    if paragraf[-4:] == '<br>':
        paragraf = paragraf[:-4]
    return paragraf.split('<br>')


def get_words(sentence):
    prepared_text = ''
    for letter in sentence:
        if (letter.isalpha() or letter.isdigit() or letter == ' '):
            prepared_text += letter
    return prepared_text.split()

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

    def create_statistics(self, elements):
        statistics = dict()
        letters_statistics = dict()
        total = 0
        for element, address in elements:
            if element not in statistics:
                statistics[element] = {'addresses': [], 'text': element, 'n_v': word_numerical_value(element),
                                       'energy': e(element), 'length': len(element), 'count': 0}
            statistics[element]['count'] += 1
            statistics[element]['addresses'].append(address)
            # формирование статистики по буквам
            letter = element[0].upper()
            if letter not in letters_statistics:
                letters_statistics[letter] = {'count': 0, 'percent': 0, 'words': [], 'adresses': []}
            total += 1
            letters_statistics[letter]['count'] += 1
            letters_statistics[letter]['words'].append(element)
            letters_statistics[letter]['adresses'].append(address)
            letters_statistics[letter]['percent'] = round((letters_statistics[letter]['count'] / total) * 100, 2)
        return list(statistics.values()), letters_statistics

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
        self.action_split_analizer.triggered.connect(self.split_analizer)

    def split_analizer(self):
        data = dict()
        setting_wnd = self.main_wnd.text_spliter_settings_form
        text = self.textEdit.toPlainText()
        if setting_wnd.wordCheckBox.isChecked():
            tree = get_areas(text)
            for area_number in range(len(tree)):
                tree[area_number] = get_paragraphs(tree[area_number])
                for paragraph_number in range(len(tree[area_number])):
                    tree[area_number][paragraph_number] = get_sentences(tree[area_number][paragraph_number])
                    for sentence_number in range(len(tree[area_number][paragraph_number])):
                        tree[area_number][paragraph_number][sentence_number] = get_words(
                            tree[area_number][paragraph_number][sentence_number])
            '''Получение адресов слов'''
            elements = []
            for area_number in range(len(tree)):
                for paragraph_number in range(len(tree[area_number])):
                    for sentence_number in range(len(tree[area_number][paragraph_number])):
                        for word_number in range(len(tree[area_number][paragraph_number][sentence_number])):
                            address = f'{area_number + 1}:{paragraph_number + 1}:{sentence_number + 1}:{word_number + 1}'
                            element = tree[area_number][paragraph_number][sentence_number][word_number]
                            elements.append((element, address))
            data['words'] = dict()
            data['words']['elements'], data['words']['letter_statistics'] = self.create_statistics(elements)
            data['words']['title'] = 'Разбиение по словам'

# если выбрали разбиение по предложениям
        if setting_wnd.sentenceCheckBox.isChecked():
            tree = get_areas(text)
            for area_number in range(len(tree)):
                tree[area_number] = get_paragraphs(tree[area_number])
                for paragraph_number in range(len(tree[area_number])):
                    tree[area_number][paragraph_number] = get_sentences(tree[area_number][paragraph_number])
            '''Получение адресов предложений'''
            elements = []
            for area_number in range(len(tree)):
                for paragraph_number in range(len(tree[area_number])):
                    for sentence_number in range(len(tree[area_number][paragraph_number])):
                        address = f'{area_number + 1}:{paragraph_number + 1}:{sentence_number + 1}'
                        element = tree[area_number][paragraph_number][sentence_number]
                        elements.append((element, address))
            data['sentences'] = dict()
            data['sentences']['elements'], data['sentences']['letter_statistics'] = self.create_statistics(elements)
            data['sentences']['title'] = 'Разбиение по предложениям'


        path = create_report('text_analyze_report.html', data=data)
        webbrowser.open(path)
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


