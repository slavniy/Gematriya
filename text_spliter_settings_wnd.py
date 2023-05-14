from PyQt5.QtWidgets import QMainWindow
from text_spliter_settings_form import Ui_Form


class TextSpliterSettingsWindow(QMainWindow, Ui_Form):
    """Класс виджета настроек разбиения текста"""
    def __init__(self, main_wnd: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.main_wnd = main_wnd




