import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QPushButton,\
    QLineEdit, QComboBox, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from main import MainWindow
import Dialogs
import re


class PdfDialog(QtWidgets.QDialog, MainWindow):

    def __init__(self, parent=None):

        # next_method is a pointer to a method run after the data has been retrieved by the dialog

        QtWidgets.QDialog.__init__(self, parent)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        layout = QtWidgets.QVBoxLayout()

        self.pricelist_label = QtWidgets.QLabel("Insert Pricelist Title: ")
        self.pricelist_entry = QtWidgets.QLineEdit()
        self.pricelist_text = ""

        self.depot_label = QtWidgets.QLabel("Insert INCOTERM eg. exw singapore: ")
        self.depot_entry = QtWidgets.QLineEdit()
        self.depot_text = ""

        self.made_in_label = QtWidgets.QLabel("Made in: ")
        self.made_in_entry = QtWidgets.QLineEdit()
        self.made_in_text = ""

        self.valid_from_label = QtWidgets.QLabel("Validity eg. until 31 8 2019:")
        self.valid_from_entry = QtWidgets.QLineEdit()
        self.valid_from_text = ""

        self.output = {}

        hlayout = QtWidgets.QHBoxLayout()

        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.clicked.connect(self.ok_pressed)

        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close_pressed)

        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.close_button)

        layout.addWidget(self.pricelist_label)
        layout.addWidget(self.pricelist_entry)
        layout.addWidget(self.depot_label)
        layout.addWidget(self.depot_entry)
        layout.addWidget(self.made_in_label)
        layout.addWidget(self.made_in_entry)
        layout.addWidget(self.valid_from_label)
        layout.addWidget(self.valid_from_entry)
        layout.addLayout(hlayout)
        self.setLayout(layout)

    def __getitem__(self, item):
        return self.output[item]

    def ok_pressed(self):

        self.pricelist_text = self.pricelist_entry.text()
        self.depot_text = self.depot_entry.text()
        self.made_in_text = self.made_in_entry.text()
        self.valid_from_text = self.valid_from_entry.text()
        self.output = {'title': self.pricelist_text, 'depot': self.depot_text, 'made_in': self.made_in_text,
                       'valid_from': self.valid_from_text}
        self.hide()

    def close_pressed(self):
        self.hide()
        del self


class FilterDialog(QtWidgets.QDialog, MainWindow):

    filter_signal = pyqtSignal(int)
    filter_clear = pyqtSignal(int)

    def __init__(self, data, parent=None):

        self.data = data  # Column data frame, data is always the same from when the object is created
        self.filtered = False
        self.just_cleared = False
        self.number = int()
        self.indices = [i for i in range(self.data.shape[0])]  # All indices
        self.values = []
        self.check_box_texts = list(set(map(str, [v for i, v in enumerate(self.data)])))  # Start with all values
        self.check_box_indices = set([i for i, v in enumerate(self.data)])
        self.check_selection = False

        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("""
                QDialog{
                    background-color:#aaa;
                    border: 1px solid black;
                }
                QLabel{ 
                    font-size: 12px;
                    font-weight: bold;
                }   
                """)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.title = QtWidgets.QLabel("Filter: ")

        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setPlaceholderText("Search")
        self.input_line.textChanged.connect(self.find_values)

        self.select_all_checkbox = QtWidgets.QCheckBox("Select/Deselect All")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_checkboxes)

        self.list = QtWidgets.QListWidget()
        self.list.itemClicked.connect(self.get_checkbox_states)
        self.generate_list([v for i, v in enumerate(self.data)])

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(10, 0, 10, 0)
        hlayout.setSpacing(10)

        self.close = QtWidgets.QPushButton("Close")
        self.close.clicked.connect(self.close_dialog)

        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.clicked.connect(self.ok_pressed)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_pressed)

        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.clear_button)
        hlayout.addWidget(self.close)

        layout.addWidget(self.title)
        layout.addWidget(self.input_line)
        layout.addWidget(self.select_all_checkbox)
        layout.addWidget(self.list)
        layout.addLayout(hlayout)
        self.setLayout(layout)

        # Use groupbox for border

    def set_x_y(self, x, y):
        self.x = x
        self.y = y
        self.move(x, y)

    def find_values(self):
        # Runs every time a character has changed in the entry box

        text = self.input_line.text()

        if text == '':
            self.generate_list([v for i, v in enumerate(self.data)])
            self.indices = [i for i in range(self.data.shape[0])]  # All indices
            return

        indices = set()
        values = set()

        # Find index and corresponding value in data rows
        for i, v in enumerate(self.data):
            if re.search(text, str(v), re.IGNORECASE):
                indices.add(i)
                values.add(v)

        self.filtered = True
        self.indices = indices
        self.values = values

        self.indices = set(self.indices)

        print("Found values updated, filter num: " + str(self.number))

        self.generate_list(list(values))

    # @pyqtSlot(QListWidgetItem) Not needed but it acts as a slot
    def get_checkbox_states(self, item):

        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

        self.check_box_texts = []

        for i in range(self.list.count()):
            if self.list.item(i).checkState() == QtCore.Qt.Checked:
                self.check_box_texts.append(self.list.item(i).text())

        self.check_box_indices = set()

        for i, v in enumerate(self.data):
            if v in self.check_box_texts:
                self.check_box_indices.add(i)

        print("Checkboxes updated, filter num: " + str(self.number))

        self.indices = self.check_box_indices

    def generate_list(self, values):

        self.list.clear()

        values = sorted(list(map(str, set(values))))  # Sort alphabetically

        # values is a set or a list
        for i in values:
            self.list_line(i, QtCore.Qt.Checked)

    def update_list(self, indices):
        # Make a slot so that it does this automatically once one filter has been filtered
        # self.indices = indices
        temp_data = self.data.iloc[indices]
        self.generate_list([v for i, v in enumerate(temp_data)])

    def toggle_all_checkboxes(self):
        check_state = QtCore.Qt.Checked if self.select_all_checkbox.checkState() == QtCore.Qt.Checked \
            else QtCore.Qt.Unchecked

        for i in range(self.list.count()):
            self.list.item(i).setCheckState(check_state)

        # restart with all checkbox values since signal doesn't run it
        self.check_box_texts = list(set(map(str, [v for i, v in enumerate(self.data)])))

    def list_line(self, text, checked):
        item = QtWidgets.QListWidgetItem()
        item.setText(str(text))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(checked)  # QtCore.Qt.Unchecked
        self.list.addItem(item)
        return item

    def ok_pressed(self):
        if self.just_cleared:
            self.filter_signal.emit(-1)
            self.just_cleared = False
        else:
            self.filter_signal.emit(self.number)

        self.hide()

    def clear_pressed(self):
        self.filter_clear.emit(self.number)
        self.input_line.setText("")
        self.just_cleared = True
        self.update_list([i for i in range(self.data.shape[0])])

    def close_dialog(self):
        self.hide()
        del self


class CurrencyDialog(QDialog, MainWindow):

    currency_inserted = pyqtSignal(float)

    def __init__(self, parent=None):

        QDialog.__init__(self, parent)

        self.layout = QVBoxLayout()

        label_1 = QLabel("Select Currency:")

        self.combo_box = QComboBox()
        self.combo_box.addItems(["USD", "SGD"])
        self.combo_box.currentIndexChanged.connect(self.select_currency)

        self.label_2 = QLabel("Insert exchange rate:")
        self.label_2.hide()
        self.entry_box = QLineEdit()
        self.entry_box.hide()

        self.hlayout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.ok_pressed)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)
        self.hlayout.addWidget(ok_button)
        self.hlayout.addWidget(close_button)

        self.layout.addWidget(label_1)
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.label_2)
        self.layout.addWidget(self.entry_box)
        self.layout.addLayout(self.hlayout)

        self.setLayout(self.layout)

    def select_currency(self):

        if self.combo_box.currentText() == "SGD":

            self.label_2.show()
            self.entry_box.show()

        else:

            self.label_2.hide()
            self.entry_box.hide()

    def ok_pressed(self):

        if self.combo_box.currentText() == "SGD":
            try:

                currency = float(self.entry_box.text())
                self.currency_inserted.emit(currency)
                self.hide()

            except ValueError:

                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setText("Could not recognize exchange rate as a number")

                if error_box.exec():
                    pass
        else:
            currency = -1
            self.currency_inserted.emit(currency)
            self.hide()
