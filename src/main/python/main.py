from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from os import environ, mkdir, path, unlink, startfile
from Table import Table
from excelSaver import ExcelSaver
from pdfGenerator import DataToPdf
import Dialogs
import pandas as pd
import ctypes
from utils import to_float, format_num
import sys
from sorting import sort_df, categorize
from filemanager import excel_to_csv


class EditButtonsWidget(QtWidgets.QWidget):

    def __init__(self, text, MainWindow, col_data, parent=None):
        super(EditButtonsWidget, self).__init__(parent)

        self.MainWindow = MainWindow
        self.values = ""
        self.text = text
        self.filtered_data = list()

        self.filter_dlg = Dialogs.FilterDialog(col_data)

        # add your buttons
        layout = QtWidgets.QHBoxLayout(self)

        # adjust spacings to your needs
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # add your widgets
        self.column_label = QtWidgets.QLabel(text)
        self.column_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Calibri")
        font.setBold(True)
        self.column_label.setFont(font)
        self.column_label.setWordWrap(True)
        self.filter_button = QtWidgets.QToolButton()
        self.filter_button.clicked.connect(self.open_filter_dialog)  # Open and run a dialog for the filter class

        icon = QtGui.QIcon("filter.ico")
        self.filter_button.setIcon(icon)

        self.filter_button.setFixedHeight(100)

        self.setStyleSheet("""
            background-color:#aaa;
        """)

        layout.addWidget(self.column_label)
        layout.addWidget(self.filter_button)

        self.setLayout(layout)

    def open_filter_dialog(self):  # Needs to give an appropriate response given the clicked column (22 columns)
        x = self.filter_button.x() + self.x() + self.MainWindow.x() + 47
        y = self.filter_button.y() + self.MainWindow.y() + 163
        self.filter_dlg.set_x_y(x, y)

        if self.filter_dlg.exec_():
            pass


class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, temp_check_list):

        super().__init__()
        self.temp_check_list = temp_check_list

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily("Calibri")
        font.setBold(True)
        self.setFont(font)
        # self.check_box.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.stateChanged.connect(self.check)

        self.setStyleSheet("""
                    background-color:#aaa;
                """)

    def check(self):

        for item in self.temp_check_list:
            if self.isChecked():
                item.setCheckState(True)
            else:
                item.setCheckState(False)


class FilterTable(Table):

    def __init__(self, headers, data, mainWindow, linker_function):
        super().__init__(text="Reset Filter Table", title="FILTER TABLE")

        self.connectPushButton("Reset Filter Table", self.reset_table)
        self.table.setWordWrap(True)

        self.mainWindow = mainWindow
        self.headers = headers
        self.header_widgets = []
        self.filter_sequence = []
        self.full_data = data
        self.data = data[headers]
        self.temp_check_list = list()
        self.linker_function = linker_function

        self.table.setColumnCount(len(headers) + 1)
        self.table.setRowCount(len(self.data)+1)
        self.header_widgets = self._set_headers(headers)
        self.insert_rows(self.data)

        self.insert_item = CheckBox(self.temp_check_list)
        self.table.setCellWidget(0, self.table.columnCount() - 1, self.insert_item)

        self.table.setRowHeight(0, 100)

    def _set_headers(self, headers):

        # Creates a header for each column with an internal widget defined by EditButtonsWidget

        header_widgets = []

        # For loop to generate header label + filter
        for i, header in enumerate(headers):

            temp_head = EditButtonsWidget(header, self.mainWindow, self.data[header])
            temp_head.filter_dlg.number = i
            temp_head.filter_dlg.filter_signal.connect(self.update_table)
            temp_head.filter_dlg.filter_clear.connect(self.clear_filter)

            header_widgets.append(temp_head)
            self.table.setCellWidget(0, i, temp_head)

        if "Rotterdam" in self.mainWindow.origin_path:
            print("Origin Rotterdam")
            self.table.setColumnWidth(9, 250)
        self.table.resizeColumnsToContents()

        return header_widgets

    def insert_rows(self, data):
        super().insert_rows(data, set_row_count=False, start_row=1)
        self.temp_check_list = []

        # CHECKBOXES: Future create checkbox cell widget class

        last_column = len(self.headers)

        for r in range(self.table.rowCount()):

            temp_check = QtWidgets.QCheckBox()
            temp_check.setCheckState(QtCore.Qt.Unchecked)

            if r % 2 == 1:
                temp_check.setStyleSheet("background-color: #bbb")

            self.table.setCellWidget(r+1, last_column, temp_check)
            self.temp_check_list.append(temp_check)

    def get_indices(self, sequence):
        # To be run every time table is filtered
        # Returns a three dimensional list[filters[data[row_index, value]
        # Which represents the filtered data for each column

        # TODO CHECK
        # Every filter should save its search so that it can do it again when a filter is cleared
        # This should be independent of what is shown on the list view update_list_values() already does that
        # Should be changed with a method that is called on each filter
        # that returns its indices based on their saved search and this is done in the progressive order dictated by the
        # sequence

        # Get the data of the filtered that has been used first
        indices = self.header_widgets[sequence[0]].filter_dlg.indices
        print(indices)

        try:
            print("Sequence")
            print(sequence)
            for s in sequence[1:]:
                filter_indices = self.header_widgets[s].filter_dlg.indices
                indices = set(indices) & set(filter_indices)  # Only find common values
        except IndexError:
            pass

        return list(indices)

    def update_list_values(self, indices):

        for n in self.header_widgets:
            n.filter_dlg.update_list(indices)

    @pyqtSlot(int)
    def clear_filter(self, filter_num):
        self.filter_sequence.remove(filter_num)

        def remove_duplicates(sequence):
            seen = []
            result = []
            for s in sequence:
                if s not in seen:
                    result.append(s)
                    seen.append(s)

            return result

        self.filter_sequence = remove_duplicates(self.filter_sequence)

        print("Filter sequence number")
        print(self.filter_sequence)

        # for i in self.filter_sequence:
        #     self.header_widgets[i].filter_dlg.find_values()

    @pyqtSlot(int)  # Receives the number of the filter that has been updated
    def update_table(self, filter_num):
        # Called every time ok is pressed on the filter dialog
        # Changes attribute data

        self.data = self.full_data[self.headers]

        # Gets the rows of data based on the indices
        if filter_num != -1:
            self.filter_sequence.append(filter_num)

        indices = self.get_indices(self.filter_sequence)
        self.data = self.data.iloc[indices]

        # Ensure other filters are updated
        if filter_num != -1:
            self.update_list_values(indices)

        self.table.setRowCount(1 + self.data.shape[0])
        self.insert_rows(self.data)

        # Creates a new select all check_box with the right reference to the row checkboxes
        self.insert_item = CheckBox(self.temp_check_list)
        self.table.setCellWidget(0, self.table.columnCount() - 1, self.insert_item)

        self.linker_function(self.data)

    def reset_table(self):
        self.__init__(self.headers, self.full_data, self.mainWindow, self.linker_function)
        self.mainWindow.grid.addWidget(self, 2, 0, 1, 1)

    def to_boolean_list(self):

        check_states = list()

        for check_box in self.temp_check_list:
            if check_box.isChecked():
                check_states.append(True)
            else:
                check_states.append(False)

        return check_states


class PreviewTable(Table):
    def __init__(self, table_columns, curr_df, data, exw, msp, filter_table):
        super().__init__(text="Insert Data", title="PREVIEW TABLE")
        self.table.setWordWrap(True)
        self.table.cellChanged.connect(self.cell_changed)
        # self.table.cellActivated.connect(self.cell_selected)

        self.addPushButton("Sort")
        self.addPushButton("Clear Preview Table")
        self.connectPushButton("Insert Data", self.insert_data)
        self.connectPushButton("Sort", self.sort_by_class)
        self.connectPushButton("Clear Preview Table", self.clear)

        self.table_columns = table_columns + ["Delete"]
        self.filter_table = filter_table
        self.origin_exw = exw
        self.origin_msp = msp
        self.lines = curr_df
        self.data = data
        self.delete_buttons = list()

        self.set_headers(self.table_columns)

        self.layout.addWidget(self.table, 1, 0, 1, 2)

        self.setLayout(self.layout)

    def cell_changed(self):

        try:
            # Select highlighted items
            item = self.table.selectedItems()[0]
            row = item.row()

            # Calculate price

            # Temporary if-else remove when msp columns in singapore are merged
            old = self.to_float(self.data[self.origin_msp].values[row])
            new = self.to_float(item.text())
            price = ((new-old)/old)*100

            # Select perc column and update value
            perc_item = self.table.item(row, item.column()+1)
            price = "{perc:.2f} %".format(perc=price)
            perc_item.setText(price)

            # Update data in frame
            self.data["Manual Price"].values[row] = str(item.text())
            self.data["Percentage markup"].values[row] = str(price)

        except IndexError:
            pass
        except TypeError:
            pass

    def to_float(self, val):
        try:
            val = float(val)
        except ValueError:
            val = val.replace(",", "")
            val = val[:val.find(".")]
            try:
                val = float(val)
            except ValueError:
                pass
        return val

    def insert_data(self):
        # NOTE points to filter table

        # Get list of checked checkboxes in the filter table
        self.line_select = self.filter_table.to_boolean_list()[:-1]

        self.new_lines = self.lines.loc[self.line_select]
        self.data = self.data.append(self.new_lines)
        self.data.reset_index(drop=True, inplace=True)

        # insert initial percentage markup
        for i, val in enumerate(self.data.values):
            old = self.to_float(self.data.at[i, self.origin_msp])
            new = self.to_float(self.data.at[i, self.origin_exw])
            price = ((new - old) / new) * 100
            self.data["Percentage markup"].values[i] = "{perc:.2f} %".format(perc=price)

        self.insert_rows(self.data)

    def insert_rows(self, data):
        super().insert_rows(data)

        class del_button_widget():
            def __init__(self, f, row):
                self.f = f
                self.row = row
                self.button = QtWidgets.QPushButton("Delete")
                self.button.clicked.connect(self.activate)
                self.activated = False

            def activate(self):
                self.activated = True
                self.f(self.row)

        col = self.headers.index("Delete")

        for row in range(len(self.delete_buttons), data.shape[0]):
            button = del_button_widget(self.remove_row, row)

            self.table.setCellWidget(row, col, button.button)
            self.delete_buttons.append(button)

        # for btn in self.delete_buttons:
        #     print("Button : {r}".format(r = btn.row))
        #     print(data.iloc[[btn.row]])

    def remove_row(self, row):

        self.table.removeRow(row)
        self.data.reset_index(drop=True, inplace=True)
        self.data.drop(row, inplace=True)
        self.delete_buttons.pop(row)  # Remove the object in the list

        # Update the row numbers of the delete buttons so that they refer to the right row
        for r, btn in enumerate(self.delete_buttons):
            btn.row = r

    def sort_by_class(self):  # and display
        self.data = sort_df(self.data)
        # self.data.to_excel("sorted.xls")
        super().clear()  # Clear table
        self.delete_buttons = list()  # Reset Buttons
        self.insert_rows(self.data)  # Reinsert rows with sorted data

    def clear(self):
        super().clear()
        self.table.setRowCount(0)
        self.data = pd.DataFrame()
        # self.line_select = [False for i in self.data.iterrows()]
        self.delete_buttons = list()


class MainWindow(QMainWindow):

    def __init__(self):
        # This class becomes an instance of MainWindow, all QMainWindow attributes and functions can be referred by self
        super().__init__()
        self.setGeometry(20, 30, 1580, 800)  # Self refers to QMainWindow object functions and the functions defined in this class
        self.setObjectName("MainWindow")
        self.setWindowTitle("Price List")

        # Class variables

        settings_path = path.join(path.dirname(__file__), 'settings.txt')

        with open(settings_path, "r") as settings:
            lines = settings.readlines()
            self.sheet_num = tuple([n.strip() for n in lines[0].split("=")[1].split(",")])
            self.sheet_names = tuple([n.strip() for n in lines[1].split("=")[1].split(",")])
            self.excel_names = tuple([n.strip() for n in lines[2].split("=")[1].split(",")])
            self.server_path = lines[3].split("=")[1].strip() # path.join(environ['HOMEPATH'], 'Desktop', 'PricelistData')

        print(self.sheet_num)
        print(self.sheet_names)
        print(self.excel_names)
        print(self.server_path)

        self.save_dir = path.join(environ["HOMEPATH"] + "Desktop")  # Mac environ["HOME"] + "\\Desktop"
        self.origin_path = ""
        self.origin_exw = ""
        self.origin_msp = ""
        self.first_run = True
        self.exchange_rate = None  # Will become float if set
        self.filter_df, self.prev_df = [pd.DataFrame(data=None)] * 2
        # Layout

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.grid = QtWidgets.QGridLayout(self.centralwidget)

        # Widgets
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.title_label = QtWidgets.QLabel("ESSENZA PRICELIST")
        self.title_label.setStyleSheet("font-size: 20pt; margin-top: 10px")
        self.horizontal_layout.addWidget(self.title_label, QtCore.Qt.AlignLeft)

        self.origin_layout = QtWidgets.QVBoxLayout()

        self.update_button = QtWidgets.QPushButton("Update Data")
        self.update_button.setFixedWidth(120)
        self.update_button.clicked.connect(self.update_excel_data)
        self.origin_layout.insertWidget(0, self.update_button, 0, QtCore.Qt.AlignRight)

        self.origin_label = QtWidgets.QLabel("Select Origin:")
        self.origin_layout.insertWidget(1, self.origin_label, 0, QtCore.Qt.AlignLeft)

        self.origin_box = QtWidgets.QComboBox()
        self.origin_box.setFixedWidth(120)
        self.origin_box.addItems(["Singapore", "Rotterdam", "Italy"])
        self.origin_box.activated.connect(self.select_origin)
        self.select_origin()
        self.origin_layout.insertWidget(2, self.origin_box, 0, QtCore.Qt.AlignRight)

        self.exchange_rate_label = QtWidgets.QLabel("Displaying prices in USD")
        self.origin_layout.insertWidget(3, self.exchange_rate_label, 0, QtCore.Qt.AlignRight)

        self.horizontal_layout.addLayout(self.origin_layout)
        self.grid.addLayout(self.horizontal_layout, 0, 0, 1, 1)

        self.filter_table = FilterTable(self.filter_table_columns, self.curr_df, self, self.update_preview_data)
        self.grid.addWidget(self.filter_table, 2, 0, 1, 1)

        self.prev_table = PreviewTable(self.preview_table_columns, self.curr_df, self.prev_df, self.origin_exw,
                                       self.origin_msp, self.filter_table)
        self.grid.addWidget(self.prev_table, 3, 0, 1, 1)

        self.excel_button = QtWidgets.QPushButton("Save to Excel")
        self.excel_button.setFixedWidth(120)
        self.excel_button.clicked.connect(self.print_to_excel)
        self.grid.addWidget(self.excel_button, 4, 0, 1, 1, QtCore.Qt.AlignRight)

        self.pdf_button = QtWidgets.QPushButton("Save to PDF")
        self.pdf_button.setFixedWidth(120)
        self.pdf_button.clicked.connect(self.print_to_pdf)
        self.grid.addWidget(self.pdf_button, 5, 0, 1, 1, QtCore.Qt.AlignRight)

        # End
        self.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(self)

    @pyqtSlot(float)
    def get_currency(self, exchange):
        self.exchange_rate = exchange

    def select_origin(self):

        def to_float(val):
            try:
                val = float(val)
            except ValueError:
                val = val.replace(",", "")
                val = val[:val.find(".")]
                val = float(val)
            return val

        origin = self.origin_box.currentText()
        self.origin_path = path.join(self.server_path, self.origin_box.currentText() + '.csv')

        if origin == "Singapore":

            # Get the currency

            dialog_currency = Dialogs.CurrencyDialog()
            dialog_currency.currency_inserted.connect(self.get_currency)

            if not self.first_run:
                if dialog_currency.exec():
                    pass

            # Get the data

            self.origin_path = path.join(self.server_path, "Singapore.csv") # Needed for the pdf generator

            try:
                sg_df = pd.read_csv(self.origin_path, sep=',', encoding="ISO-8859-1")
            except FileNotFoundError:
                message_box = QMessageBox()
                message_box.setText("File Not Found: Select Excel File")
                message_box.setIcon(QMessageBox.Critical)

                if message_box.exec():
                    pass

                self.update_excel_data()

            sg_df = pd.read_csv(self.origin_path, sep=',', encoding="ISO-8859-1")

            rtd_df = pd.read_csv(path.join(self.server_path, "Rotterdam.csv"), sep=',', encoding="ISO-8859-1")

            g_df = pd.read_csv(path.join(self.server_path, "Greases.csv"), sep=',', encoding="ISO-8859-1")

            # COMBINE COLUMNS

            merged_lt_pcs = pd.concat([sg_df["LT/PCS"], rtd_df["LT/PCS"], g_df["KG/PCS"]])
            merged_lt_pcs = merged_lt_pcs.astype(str)

            merged_lt_su = pd.concat([sg_df["LT/SU"], rtd_df["LT/SU"], g_df["KG/SU"]])
            merged_lt_su = merged_lt_su.astype(str)

            sg_df = sg_df.drop(columns=["LT/PCS", "LT/SU", "DISTRIBUTOR EXW ROTTERDAM (EUR/SU)", "DISTRIBUTOR EXW SINGAPORE (SGD/SU)"])
            rtd_df = rtd_df.drop(columns=["LT/PCS", "LT/SU", "DISTRIBUTOR EXW ROTTERDAM (EUR/SU)", "DISTRIBUTOR EXW SINGAPORE (SGD/SU)"])
            g_df = g_df.drop(columns=["KG/PCS", "KG/SU", "DISTRIBUTOR EXW ROTTERDAM (EUR/SU)", "DISTRIBUTOR EXW SINGAPORE (SGD/SU)"])

            self.curr_df = pd.concat([sg_df, rtd_df, g_df], sort=False)
            self.curr_df["LT/PCS"] = merged_lt_pcs
            self.curr_df["LT/SU"] = merged_lt_su

            self.origin_exw = "DISTRIBUTOR EXW SINGAPORE (USD/SU)"
            self.origin_msp = "MSP EXW SINGAPORE (USD/SU)"

            if self.exchange_rate is not None:

                if self.exchange_rate != -1.0:

                    self.exchange_rate_label.setText("Exchange rate USD to SGD: " + str(self.exchange_rate))

                    exw_col = "DISTRIBUTOR EXW SINGAPORE (USD/SU)"
                    msp_col = "MSP EXW SINGAPORE (USD/SU)"

                    self.curr_df[exw_col] = self.curr_df[exw_col].apply(to_float)
                    self.curr_df[msp_col] = self.curr_df[msp_col].apply(to_float)

                    self.curr_df[exw_col] *= self.exchange_rate
                    self.curr_df[msp_col] *= self.exchange_rate

                    self.curr_df[exw_col] = self.curr_df[exw_col].apply(format_num)
                    self.curr_df[msp_col] = self.curr_df[msp_col].apply(format_num)
                    self.curr_df[exw_col] = self.curr_df[exw_col].apply(to_float)
                    self.curr_df[msp_col] = self.curr_df[msp_col].apply(to_float)

                    self.curr_df.rename(columns={exw_col: "DISTRIBUTOR EXW SINGAPORE (SGD/SU)",
                                                 msp_col: "MSP EXW SINGAPORE (SGD/SU)"}, inplace=True)

                    self.origin_exw = "DISTRIBUTOR EXW SINGAPORE (SGD/SU)"
                    self.origin_msp = "MSP EXW SINGAPORE (SGD/SU)"

                else:

                    self.exchange_rate = 1

                    self.exchange_rate_label.setText("Displaying prices in USD")

                    if "DISTRIBUTOR EXW SINGAPORE (SGD/SU)" not in self.curr_df.columns:
                        exw_col = "DISTRIBUTOR EXW SINGAPORE (USD/SU)"
                        msp_col = "MSP EXW SINGAPORE (USD/SU)"

                    self.curr_df[exw_col] = self.curr_df[exw_col].apply(to_float)
                    self.curr_df[msp_col] = self.curr_df[msp_col].apply(to_float)

                    self.curr_df[exw_col] *= self.exchange_rate
                    self.curr_df[msp_col] *= self.exchange_rate

                    self.curr_df[exw_col] = self.curr_df[exw_col].apply(format_num)
                    self.curr_df[msp_col] = self.curr_df[msp_col].apply(format_num)
                    self.curr_df[exw_col] = self.curr_df[exw_col].apply(to_float)
                    self.curr_df[msp_col] = self.curr_df[msp_col].apply(to_float)

                    self.curr_df.rename(columns={exw_col: "DISTRIBUTOR EXW SINGAPORE (USD/SU)",
                                                 msp_col: "MSP EXW SINGAPORE (USD/SU)"}, inplace=True)

                    self.origin_exw = "DISTRIBUTOR EXW SINGAPORE (USD/SU)"
                    self.origin_msp = "MSP EXW SINGAPORE (USD/SU)"

            self.curr_df['Manual Price'] = self.curr_df[self.origin_exw]
            self.curr_df['Percentage markup'] = '0'

            self.curr_df.reset_index(drop=True, inplace=True)

            col_list = ["MSP EXW ROTTERDAM (EUR/SU)",
                        "Unnamed: 22",
                        "Percentage Markup"]

            cols = self.curr_df.columns.tolist()
            cols = cols[:10] + cols[-2:] + cols[10:-2]

        elif origin == "Rotterdam":

            self.exchange_rate_label.setText("Displaying prices in EUR")

            self.origin_exw = "DISTRIBUTOR EXW ROTTERDAM (EUR/SU)"
            self.origin_msp = "MSP EXW ROTTERDAM (EUR/SU)"

            rtd_df = pd.read_csv(self.origin_path, sep=',', encoding="ISO-8859-1")
            g_df = pd.read_csv(path.join(self.server_path, "Greases.csv"), sep=',', encoding="ISO-8859-1")

            merged_lt_pcs = pd.concat([rtd_df["LT/PCS"], g_df["KG/PCS"]])
            merged_lt_pcs = merged_lt_pcs.astype(str)

            merged_lt_su = pd.concat([rtd_df["LT/SU"], g_df["KG/SU"]])
            merged_lt_su = merged_lt_su.astype(str)

            g_df = g_df.drop(columns=["KG/PCS", "KG/SU"])
            rtd_df = rtd_df.drop(columns=["LT/PCS", "LT/SU"])

            self.curr_df = pd.concat([rtd_df, g_df], sort=False)
            self.curr_df["LT/PCS"] = merged_lt_pcs
            self.curr_df["LT/SU"] = merged_lt_su
            self.curr_df['Manual Price'] = self.curr_df[self.origin_exw]
            self.curr_df['Percentage markup'] = '0'
            self.curr_df.reset_index(drop=True, inplace=True)

            col_list = ["DISTRIBUTOR EXW SINGAPORE (USD/SU)",
                        "DISTRIBUTOR EXW SINGAPORE (SGD/SU)",
                        "MSP EXW SINGAPORE (USD/SU)",
                        "Percentage Markup"]

            cols = self.curr_df.columns.tolist()
            cols = cols[:10] + cols[-2:] + cols[10:-2]

        elif origin == "Italy":

            self.exchange_rate_label.setText("Displaying prices in EUR")

            self.origin_exw = "DISTRIBUTOR EXW ITALY (EUR/SU) EXC. ACCISA"
            self.origin_msp = "MSP EXW ITALY (EUR/SU)"
            self.curr_df = pd.read_csv(self.origin_path, sep=',', encoding="ISO-8859-1")
            self.curr_df['Manual Price'] = self.curr_df[self.origin_exw]
            self.curr_df['Percentage markup'] = '0'

            col_list = ["DISTRIBUTOR EXW SINGAPORE (USD/SU) EXC. ACCISA",
                        "DISTRIBUTOR EXW SINGAPORE (SGD/SU) EXC. ACCISA",
                        "MSP EXW SINGAPORE (USD/SU)"]
            cols = self.curr_df.columns.tolist()

        for c in col_list:
            try:
                cols.remove(c)
            except ValueError:
                pass

        self.curr_df = self.curr_df[cols]

        self.filter_table_columns = ["PRODUCT CODE", "PACK CODE", "FAMILY NAME", "PRODUCT NAME",
                                     "GRADE", "TYPE", "PACK (SU=SELLING UNIT)", self.origin_exw, "PRODUCT CLASS",
                                     "SPECIFICATION LEVEL", self.origin_msp]

        self.preview_table_columns = ["SYSPRO CODE", "SYSPRO NAME", "PACK (SU=SELLING UNIT)",
                                      "SPECIFICATION LEVEL",  self.origin_msp, self.origin_exw, 'Manual Price', 'Percentage markup']

        self.print_pdf_columns = ["SYSPRO CODE", "SYSPRO NAME", "TYPE", "PACK (SU=SELLING UNIT)",
                                  "SPECIFICATION LEVEL", "Manual Price"]

        self.filter_df = self.curr_df[self.filter_table_columns]

        if self.first_run is False:

            self.reset_tables()
            # Inform the user
            if self.first_run is False:
                update_box = QMessageBox()
                update_box.setText("Table Updated.")
                p = QtGui.QPixmap()
                p.load("info.png")
                update_box.setIconPixmap(p)

                if update_box.exec():
                    pass

        self.first_run = False

    def print_to_pdf(self):
        data = sort_df(self.prev_table.data)  # In case user didn't press sort by class
        dataframes = categorize(data)
        # typed_data = ["PRICELIST TITLE", "EXW DEPOT", "MADE IN LOCATION", "1 JUNE 2019"]
        typed_data = Dialogs.PdfDialog()

        if typed_data.exec_():
            pass

        # TODO: Convert the whole thing to use a context manager or use finally statement
        try:
            pdf = DataToPdf(dataframes, self.print_pdf_columns, self.origin_path, typed_data, self.exchange_rate)
            pdf.export("TestPDF.pdf")
            startfile("TestPDF.pdf")
        except PermissionError:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setText("Please close TestPDF and try again.")

            if error_box.exec():
                pass

    def print_to_excel(self):
        saver = ExcelSaver(self.save_dir)
        data = self.prev_table.data
        saver.save(data)
        startfile("TESTEXCEL.xlsx")

    def update_excel_data(self):
        server_path = QFileDialog.getOpenFileName(self, "SELECT DATA FOLDER", environ["HOMEPATH"],
                                                  "Excel files (*.csv *.xlsx *.xls)")

        if server_path:
            self.server_path = path.dirname(server_path[0])

        print(self.server_path)

        excel_to_csv(self.server_path, self.sheet_num, self.sheet_names, self.excel_names)

        self.server_path = path.join(self.server_path, 'PricelistData')
        print("Reselecting origin")
        self.select_origin()

    def reset_tables(self):
        self.filter_table = FilterTable(self.filter_table_columns, self.curr_df, self, self.update_preview_data)
        self.grid.addWidget(self.filter_table, 2, 0, 1, 1)

        self.prev_table = PreviewTable(self.preview_table_columns, self.curr_df, self.prev_df, self.origin_exw,
                                       self.origin_msp, self.filter_table)
        setattr(self.prev_table, "lines", self.curr_df)
        self.grid.addWidget(self.prev_table, 3, 0, 1, 1)

    def update_preview_data(self, filtered_dataframe):
        '''
        Linker function for Filter Table,
        receives the filtered data frame from the class and
        current complete data frame based on the selected origin.

        It then prepares the data in the Preview Table class, ready to be added when the button is pressed

        Done with the purpose of abstracting this operation and make it easier to read and modify at a higher level
        '''

        print("")
        print("")
        print("NEW TABLE UPDATE")
        print("")
        print("")

        new_lines = self.all_columns(self.curr_df, filtered_dataframe)

        setattr(self.prev_table, "lines", new_lines)

    def all_columns(self, full_data, data):
        # Returns a dataframe with all columns based with only the rows that have been selected after filtering

        return pd.DataFrame(full_data.iloc[[r[0] for r in data.iterrows()]])


if __name__ == '__main__':
    appctxt = ApplicationContext()

    window = MainWindow()
    window.show()

    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
