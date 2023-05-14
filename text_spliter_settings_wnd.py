from PyQt5.QtWidgets import QMainWindow
from text_spliter_settings_form import Ui_Form


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

    def word_clicked(self):
        if self.wordCheckBox.isChecked():
            print('Добавили разбиение по словам!')
        else:
            print('Убрали разбиение по словам!')

    def sentence_clicked(self):
        if self.sentenceCheckBox.isChecked():
            print('Добавили разбиение по предложениям!')
        else:
            print('Убрали разбиение по предложениям!')

    def paragraf_clicked(self):
        if self.paragrafCheckBox.isChecked():
            print('Добавили разбиение по абзацам!')
        else:
            print('Убрали разбиение по абзацам!')

    def area_clicked(self):
        if self.areaCheckBox.isChecked():
            print('Добавили разбиение по областям!')
        else:
            print('Убрали разбиение по областям!')




