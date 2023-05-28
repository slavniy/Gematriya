from PyQt5.QtWidgets import QMainWindow
from forms.text_spliter_settings_form import Ui_Form
import json


class TextSpliterSettingsWindow(QMainWindow, Ui_Form):
    """Класс виджета настроек разбиения текста"""

    def __init__(self, main_wnd: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_wnd = main_wnd
        self.wordCheckBox.stateChanged.connect(self.word_clicked)
        self.sentenceCheckBox.stateChanged.connect(self.sentence_clicked)
        self.paragrafCheckBox.stateChanged.connect(self.paragraf_clicked)
        self.areaCheckBox.stateChanged.connect(self.area_clicked)

    def save_state(self):
        data = {
            "words": self.wordCheckBox.isChecked(),
            "sentences": self.sentenceCheckBox.isChecked(),
            "paragrafs": self.paragrafCheckBox.isChecked(),
            "areas": self.areaCheckBox.isChecked()
        }
        with open('static/settings.json', 'w') as outfile:
            json.dump(data, outfile)

    def load_state(self):
        with open('static/settings.json') as settings:
            data = json.load(settings)
        if data["words"]:
            self.wordCheckBox.setChecked(True)
        if data["sentences"]:
            self.sentenceCheckBox.setChecked(True)
        if data["paragrafs"]:
            self.paragrafCheckBox.setChecked(True)
        if data["areas"]:
            self.areaCheckBox.setChecked(True)

    def word_clicked(self):
        # if self.wordCheckBox.isChecked():
        #     self.main_wnd.words_split = True
        # else:
        #     self.main_wnd.words_split = False
        self.save_state()

    def sentence_clicked(self):
        # if self.sentenceCheckBox.isChecked():
        #     print('Добавили разбиение по предложениям!')
        # else:
        #     print('Убрали разбиение по предложениям!')
        self.save_state()

    def paragraf_clicked(self):
        # if self.paragrafCheckBox.isChecked():
        #     print('Добавили разбиение по абзацам!')
        # else:
        #     print('Убрали разбиение по абзацам!')
        self.save_state()

    def area_clicked(self):
        # if self.areaCheckBox.isChecked():
        #     print('Добавили разбиение по областям!')
        # else:
        #     print('Убрали разбиение по областям!')
        self.save_state()
