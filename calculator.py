import webbrowser
from PyQt5 import QtWidgets
import os

from ui import Ui_MainWindow
from ui_settings import Ui_weight_settings
import e_f_fl_calculate
from report import report


def format_plus(number):
    if number == 0:
        return '0'
    else:
        return f'{number:+g}'


class WeightSettingsDialog(QtWidgets.QDialog, Ui_weight_settings):
    def __init__(self):
        super(WeightSettingsDialog, self).__init__()

        self.setupUi(self)

        self.buttonBox.accepted.connect(self.accept_data)
        self.buttonBox.rejected.connect(self.reject_data)

    def accept_data(self):
        print('a')

    def reject_data(self):
        print('r')


class CalcWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(CalcWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.menuBar.setVisible(False)

        self.weight_settings = QtWidgets.QDialog()
        self.ui_weight_settings = Ui_weight_settings()
        self.ui_weight_settings.setupUi(self.weight_settings)

        self.ui.name1.textChanged[str].connect(self.name1_on_changed)
        self.ui.name2.textChanged[str].connect(self.name2_on_changed)
        self.ui.report.clicked.connect(self.show_report)
        self.ui.weight_settings.triggered.connect(self.show_weight_settings)

        self.name1_on_changed('')
        self.name2_on_changed('')

        self.ui.version.setText('v 0.1.5')

    def name1_on_changed(self, name1):

        e = ''
        f = ''
        m = ''

        if len(name1) >= 1:
            e = f'E={format_plus(e_f_fl_calculate.e(name1))}'
            m = f'УВ={e_f_fl_calculate.m(name1)}'

        if len(name1) > 1:
            f_base = e_f_fl_calculate.f_base_letter(name1)
            f = f'F({f_base[0]})={f_base[1]}'

        self.ui.e1.setText(e)
        self.ui.f1.setText(f)
        self.ui.m1.setText(m)

        name2 = self.ui.name2.text()
        self.calc_combination(name1, name2)

    def name2_on_changed(self, name2):

        m = ''
        e = ''
        f = ''

        if len(name2) >= 1:
            e = f'E={format_plus(e_f_fl_calculate.e(name2))}'
            m = f'УВ={e_f_fl_calculate.m(name2)}'

        if len(name2) > 1:
            f_base = e_f_fl_calculate.f_base_letter(name2)
            f = f'F({f_base[0]})={f_base[1]}'

        self.ui.e2.setText(e)
        self.ui.f2.setText(f)
        self.ui.m2.setText(m)

        name1 = self.ui.name1.text()
        self.calc_combination(name1, name2)

    def calc_combination(self, name1, name2):

        if name1 == '' or name2 == '':
            f_str = ''
            fl_str = ''
            f = 0
            fl = 0
            report_visible = False
        else:
            f = e_f_fl_calculate.f(name1, name2)
            fl = e_f_fl_calculate.fl(name1, name2)
            f_str = f'F({name1}, {name2})={f}'
            fl_str = f'FL({name1}, {name2})={format_plus(fl)}'
            report_visible = True

        if abs(f) == abs(fl):
            res_str = ''
        elif abs(f) > abs(fl):
            res_str = 'Телесно-чувственное влечение преобладает над духовно-душевной близостью'
        else:
            res_str = 'Духовно-душевная близость преобладает над телесно-чувственным влечением'

        self.ui.f12.setText(f_str)
        self.ui.fl12.setText(fl_str)
        self.ui.result1.setText(res_str)
        self.ui.report.setVisible(report_visible)

    def show_report(self):
        TEMP_DIRECTORY = 'temp'
        if not os.path.exists(TEMP_DIRECTORY):
            os.makedirs(TEMP_DIRECTORY)
        file_name = os.path.join(TEMP_DIRECTORY, 'report.html')

        name1 = self.ui.name1.text()
        name2 = self.ui.name2.text()
        report_html = report(name1, name2)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(report_html)
        webbrowser.open_new_tab(file_name)

    def show_weight_settings(self):

        dialog = WeightSettingsDialog()
        dialog.show()
        dialog.exec()

