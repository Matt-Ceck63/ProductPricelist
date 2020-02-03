from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QWidget, QTableWidget, QHeaderView, QLabel, QPushButton, QTableWidgetItem
from PyQt5 import QtCore, QtGui

class Table(QWidget):  #TODO: Change to TableWrapper
    def __init__(self, parent=None, title="Title", text="button"):
        super(Table, self).__init__(parent)

        self.buttons = {}

        # Layout
        self.layout = QGridLayout()
        self.buttonLayout = QVBoxLayout()

        # adjust spacings to your needs
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.buttonLayout.setContentsMargins(0, 10, 0, 10)
        self.buttonLayout.setSpacing(1)

        # Widgets
        button = QPushButton(text)
        button.setFixedWidth(120)
        self.buttons[text] = button
        self.buttonLayout.addWidget(button)

        label = self.label(title)
        self.table = QTableWidget()

        self.layout.addLayout(self.buttonLayout, 0, 1, 1, 1)
        self.layout.addWidget(label, 0, 0, 1, 1)
        self.layout.addWidget(self.table, 1, 0, 1, 2)

        self.setLayout(self.layout)

    def label(self, title):
        label = QLabel(title)
        label.setStyleSheet("font-size: 20px")
        return label

    def connectPushButton(self, text, f):
        self.buttons[text].clicked.connect(f)

    def addPushButton(self, text):
        button = QPushButton(text)
        button.setFixedWidth(120)
        self.buttons[text] = button
        self.buttonLayout.addWidget(button)

    def set_headers(self, headers):
        self.headers = headers
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        header.setCascadingSectionResizes(False)

        for i in range(len(headers)-1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(8, QHeaderView.Stretch)

    def insert_rows(self, rows, start_row=0, set_row_count=True):

        if set_row_count:
            self.table.setRowCount(len(rows))

        for c, h in enumerate(self.headers):
            try:
                for r, v in enumerate(rows[h], start=start_row):
                    self.table.setItem(r, c, QTableWidgetItem(str(v)))

                    if (r % 2) == 0:
                        self.set_color_to_row(self.table, r, QtGui.QColor("#bbb"))

            except KeyError:
                pass

    @staticmethod
    def set_color_to_row(table, rowIndex, color):

        for j in range(table.columnCount() + 1):
            cell = table.item(rowIndex, j)
            if cell is not None:
                cell.setBackground(color)

    def clear(self):
        self.table.clearContents()
