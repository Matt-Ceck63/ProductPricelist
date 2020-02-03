import pandas as pd
from os import path, mkdir, unlink, environ
from os.path import isdir, isfile, join
from subprocess import call

save_dir = path.relpath("/")
dir_name = "Pricelist_App_Data"
sheet_num = ("1", "2", "2", "2")
sheet_names = ("Greases", "Imported", "Italy", "Singapore")
excel_names = ("Essenza Imported Pricelist Ongoing UPDATE File-Carcare.xlsx",
               "Essenza Imported Pricelist Ongoing UPDATE File-Carcare.xlsx",
               "Essenza ITALY Pricelist Ongoing UPDATE File 518 210319.xlsx",
               "Essenza Singapore Pricelist Ongoing UPDATE Files.xlsx")


def excel_to_csv(server_path, sheet_num, sheet_names, excel_names):

    # Delete old csv files already there

    for csv in sheet_names:
        file_path = join(server_path, 'PricelistData', csv + '.csv')
        try:
            if isfile(file_path):
                unlink(file_path)
        except Exception as e:
            print(e)

    # Create excel directory

    data_dir = join(server_path, 'PricelistData')

    if not isdir(data_dir):
        make_dir(server_path, "PricelistData")

    excel_names = [path.join(server_path, name) for name in excel_names]
    #sheet_names = [path.join(server_path, name) for name in sheet_names]

    # convert each sheet to csv and then read it using read_csv

    for s, e, csv_names in zip(sheet_num, excel_names, sheet_names):
        csv = path.join(data_dir, csv_names)
        call(['cscript.exe', 'ExcelToCsv.vbs', e, csv, s])
        csv_cleanup(csv + '.csv')


def make_dir(target_path, name):
    dir = join(target_path, name)
    try:
        # Create target Directory
        mkdir(dir)
        print("Directory ", dir, " Created ")
    except FileExistsError:
        print("Directory ", dir, " already exists")


def csv_cleanup(csv):
    # Cleanup extra empty columns for faster reading
    df = pd.read_csv(csv, encoding="ISO-8859-1", dtype=str)
    df = df.dropna(thresh=2)
    df = df.dropna(how='all', axis=1)
    # Removes any before or after spaces in the headers
    for cols in df.columns.tolist():
        df.rename(columns={cols: cols.strip()}, inplace=True)

    df.to_csv(csv, encoding="ISO-8859-1", index=False)


def join_csv(csv1, csv2):
    df1 = pd.read_csv(csv1, encoding="ISO-8859-1", dtype=str)
    df2 = pd.read_csv(csv2, encoding="ISO-8859-1", dtype=str)

    result = pd.concat(df1, df2)

    return result

# def excel_to_csv(self):
#
#     sheet_num = ("1", "1", "1")
#     sheet_names = ("Imported", "Italy", "Singapore")
#     excel_names = ("Essenza Imported Pricelist Ongoing UPDATE File-Carcare.xlsx",
#                    "Essenza ITALY Pricelist Ongoing UPDATE File 518 210319.xlsx",
#                    "Essenza Singapore Pricelist Ongoing UPDATE Files.xlsx")
#
#     for the_file in sheet_names:
#         file_path = path.join(self.excel_dir, the_file)
#         try:
#             if path.isfile(file_path):
#                 unlink(file_path)
#         except Exception as e:
#             print(e)
#
#     # convert each sheet to csv and then read it using read_csv
#     from subprocess import call
#
#     try:
#         # Create target Directory
#         mkdir(self.excel_dir)
#         print("Directory ", self.excel_dir, " Created ")
#     except FileExistsError:
#         print("Directory ", self.excel_dir, " already exists")
#
#     csv_dir = self.excel_dir
#     for s, e, n in zip(sheet_num, excel_names, sheet_names):
#         csv = csv_dir + n
#         call(['cscript.exe', 'ExcelToCsv.vbs', e, csv, s])
#
#         # Cleanup extra empty columns for faster reading
#         df = pd.read_csv(csv, encoding="ISO-8859-1", dtype=str)
#         df = df.dropna(thresh=2)
#         df = df.dropna(how='all', axis=1)
#         # df.to_csv(csv, encoding="ISO-8859-1", index=False)
