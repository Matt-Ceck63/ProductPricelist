# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
#
# canvas = canvas.Canvas("form.pdf", pagesize=letter)
# canvas.setLineWidth(.3)
# canvas.setFont('Helvetica', 12)
#
# canvas.drawString(30, 750, 'OFFICIAL COMMUNIQUE')
# canvas.drawString(30, 735, 'OF ACME INDUSTRIES')
# canvas.drawString(500, 750, "12/12/2010")
# canvas.line(480, 747, 580, 747)
#
# canvas.drawString(275, 725, 'AMOUNT OWED:')
# canvas.drawString(500, 725, "$1,000.00")
# canvas.line(378, 723, 580, 723)
#
# canvas.drawString(30, 703, 'RECEIVED BY:')
# canvas.line(120, 700, 580, 700)
# canvas.drawString(120, 703, "JOHN DOE")
#
# canvas.save()

# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
#
# doc = SimpleDocTemplate("simple_table.pdf", pagesize=letter)
# # container for the 'Flowable' objects
# elements = []
#
# data = [['00', '01', '02', '03', '04'],
#         ['10', '11', '12', '13', '14'],
#         ['20', '21', '22', '23', '24'],
#         ['30', '31', '32', '33', '34']]
# t = Table(data)
# t.setStyle(TableStyle([('BACKGROUND', (1, 1), (-2, -2), colors.green),
#                        ('TEXTCOLOR', (0, 0), (1, -1), colors.red)]))
# elements.append(t)
# # write the document to disk
# doc.build(elements)

from operator import itemgetter

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, \
    Table, TableStyle, Image, PageBreak

class FooterCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):


        # Footer

        page = "Page %s of %s" % (self._pageNumber, page_count)
        info1 = "Prices may change without notice. Specifications are indicative ITALCO makes no representations " \
                "or warranties"
        info2 = "of any kind of merchantability or fitness for a particular purpose of the Products."

        self.saveState()

        # Opposite x,y since landscape
        x = int(A4[1]/2)-9*mm
        y = A4[0] - 10
        self.setFont('Helvetica', 10)
        self.drawString(x, 10*mm, page)
        self.setFont('Helvetica', 7)
        self.drawString(9*mm, 12*mm, info1)
        self.drawString(9*mm, 9*mm, info2)
        self.drawImage("ITALCO.jpeg", x=A4[1] - 30*mm, y=5*mm, width=27*mm, height=11.5*mm) # heigh = width * 0.46
        self.restoreState()

class DataToPdf():
    """
    Export dictionary to a table in a PDF file.
    """

    def __init__(self, data, headers, origin, page_header_data, exchange_rate):
        """

        :param data: Table data, dictionary of sorted dataframes, every key represents a class
        :param headers: headers that are present in the dataframe to be displayed on the table
        :param origin: current select origin
        :param custom_data: list of user typed data that will be sent to the header of the pdf PAGE
        """
        units = ("USD/SU", "EUR/SU", "SGD/SU")

        self.headers = headers
        self.data = data
        self.origin = origin
        self.exchange_rate = exchange_rate
        self.page_header_data = page_header_data

    def export(self, filename, data_align='LEFT', table_halign='LEFT'):
        """
        Export the data to a PDF file.

        Arguments:
            filename - The filename for the generated PDF file.
            data_align - The alignment of the data inside the table (eg.
                'LEFT', 'CENTER', 'RIGHT')
            table_halign - Horizontal alignment of the table on the page
                (eg. 'LEFT', 'CENTER', 'RIGHT')
        """

        page_size = landscape(A4)
        doc = SimpleDocTemplate(filename, pagesize=page_size, topMargin=27*mm, leftMargin=9*mm, rightMargin=9*mm)

        story = []

        # # Header

        font_size = 2
        left = ParagraphStyle(name="left", font="Helvetica", alignment=TA_LEFT, font_size=font_size)
        right = ParagraphStyle(name="right", font="Helvetica", alignment=TA_RIGHT, font_size=font_size)

        # Table

        style = TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN',(0, 0),(0,-1), data_align),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ])

        font_size = 8  # self.__get_font_size(self.data, 10)
        converted_data = self.__convert_data(style, font_size)
        col_widths = self.__get_col_widths(font_size)
        table = Table(converted_data, colWidths=col_widths, hAlign=table_halign, repeatRows=1)
        table.setStyle(style)

        story.append(table)

        doc.multiBuild(story, canvasmaker=FooterCanvas, onFirstPage=self.header, onLaterPages=self.header)

        update_box = QMessageBox()
        update_box.setText("Successfully Saved.")
        p = QPixmap()
        p.load("info.png")
        update_box.setIconPixmap(p)

        if update_box.exec():
            pass

    def header(self, canvas, doc):
        # Header

        data = self.page_header_data

        header_list_left = ["essenza lubricants", "b>" + data['title'].upper(),
                            "b>" + data['depot'].upper()]

        header_list_right = ["LUBRICANTS", "b>" + "MADE IN " + data['made_in'].upper(),
                             "VALIDITY " + data['valid_from'].upper()]

        canvas.saveState()

        x = 12 * mm
        y = 200 * mm

        for t in header_list_left:

            if 'b>' in t:
                font = "Helvetica-Bold"
                t = t.split('>')[1]
            else:
                font = "Helvetica"

            textobject = canvas.beginText()
            textobject.setFont(font, 10)
            textobject.setTextOrigin(
                x,
                y
            )
            textobject.textLine(t)
            canvas.drawText(textobject)

            y -= 15

        y = 200 * mm

        canvas.drawImage("logo.jpg", x=(A4[1] / 2) - 15 * mm, y=A4[0] - 23 * mm, width=15 * mm, height=15 * mm)

        for t in header_list_right:

            if 'b>' in t:
                font = "Helvetica-Bold"
                t = t.split('>')[1]
            else:
                font = "Helvetica"

            textobject = canvas.beginText()
            textobject.setFont(font, 10)
            textobject.setTextOrigin(
                A4[1] - 12 * mm - stringWidth(t, font, 10),
                y
            )
            textobject.textLine(t)
            canvas.drawText(textobject)

            y -= 15

        canvas.restoreState()

    def __convert_data(self, style, font_size):
        """
        Convert the dictionary to a list of lists to create
        the PDF table.
        """

        # Start with dataframe columns (same for everyone except GREASES)

        table = []

        # Define cell styles

        centered = ParagraphStyle(name="centered", alignment=TA_CENTER, fontSize=font_size)
        left = ParagraphStyle(name="left", alignment=TA_LEFT, fontSize=font_size)
        right = ParagraphStyle(name="right", alignment=TA_RIGHT, fontSize=font_size)

        # INSERT TABLE HEADERS

        df = next(iter(self.data.values()))

        # Get headers of first data frame
        columns = list(df[self.headers].columns)

        # Modify displayed columns
        columns = ["NAME" if i == "SYSPRO NAME" else i for i in columns]
        columns.remove("Manual Price")
        if "Singapore" in self.origin:
            if self.exchange_rate:
                columns.append("SGD/SU")
            else:
                columns.append("USD/SU")
        else:
            columns.append("EUR/SU")

        temp = []
        for item in columns:
            p = Paragraph("<b>"+item+"</b>", centered)
            temp.append(p)

        table.append(temp)

        # Get the rows of data and the category name

        row = 1

        for key, df in self.data.items():

            temp = []

            # CATEGORY ROW
            p = Paragraph("<b>"+key+"</b>", left)
            temp.append(p)

            for i in range(1, len(columns)):
                temp.append(Paragraph("", centered))  # Include empty cells as recomended in documentation
            table.append(temp)
            style.add('SPAN', (0, row), (-1, row))
            row += 1

            if "GREASE" in df["PRODUCT CLASS"] :
                # Add new header
                headers = []

                for i in df.columns:
                    if i == "LT/PCS":
                        headers.append("KG/PCS")
                    elif i == "LT/PCS":
                        headers.append("KG/PCS")
                    else:
                        headers.append(i)

                table.append(headers)

            # ROWS
            for row_item in df[self.headers].values.tolist():
                """
                df[self.headers].values.tolist():
                1 - Only select the columns that we want to display in the dataframe
                2 - select the values in that dataframe
                3 - return a list of lists representing the values in each row
                """
                temp = []
                for c, i in enumerate(row_item):
                    if c == 3:  # If PACK column then center
                        p = Paragraph(str(i), centered)

                    elif c == 5:  # If price column then right
                        formatted_number = self.__format_num(str(i))
                        p = Paragraph(formatted_number, right)

                    else:
                        p = Paragraph(str(i), left)

                    temp.append(p)
                table.append(temp)

                row +=1

        return table

    def __get_col_widths(self, font_size):

        transposed = self.__transpose()

        cols = []

        print("FONT SIZE: " + str(font_size))

        # Find longest string in pixels for each column
        for col in transposed:
            col_str = list(map(str, col))
            max_len = max([stringWidth(text, 'Helvetica-Bold', font_size) for text in col_str])

            max_len = max_len if max_len < 250 else 100

            cols.append(max_len)

        tot = sum(cols)
        widths_percentage = [c/tot for c in cols]
        widths = [a*780 for a in widths_percentage]
        widths = list(map(int, widths))
        print(widths)

        return widths

    def __transpose(self):
        data_list = []

        for key, df in self.data.items():
            lists = df[self.headers].values.tolist()
            for i in lists:
                data_list.append(i)

        data_list.append(self.headers)
        transposed = list(map(list, zip(*data_list)))


        return transposed

    def __format_num(self, number):

        number = number.strip(",. ")

        # NOTE: this does not check if all digits are 0

        if '.' in number:
            dec_length = len(number.split('.')[1])
            if dec_length < 2:
                number += '0'
        else:
            number += '.00'

        # Insert commas
        if ',' not in number and len(number) > 6:
            threes = int((len(number) - 3) / 3)
            index = (len(number) - 3) % 3
            for i in range(0, threes):
                if index != 0:
                    index += (i * 3)
                    number = number[:index + i] + ',' + number[index + i:]

        return number
