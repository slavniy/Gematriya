from PyQt5.QtWidgets import QMainWindow
from forms.text_spliter_settings_form import Ui_Form
import json


class TextSpliterSettingsWindow(QMainWindow, Ui_Form):
    """Класс виджета настроек разбиения текста"""

    def __init__(self, main_wnd: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_wnd = main_wnd
        self.wordCheckBox.stateChanged.connect(self.save_state)
        self.sentenceCheckBox.stateChanged.connect(self.save_state)
        self.paragrafCheckBox.stateChanged.connect(self.save_state)
        self.areaCheckBox.stateChanged.connect(self.save_state)

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