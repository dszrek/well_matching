#!/usr/bin/python
import os
import pandas as pd

from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import QDir

from .classes import DataFrameModel, ADataFrame


PATH_PRJ = None
dlg = None
adf = None

def dlg_main(_dlg):
    """Przekazanie referencji interfejsu dockwidget'u do zmiennej globalnej."""
    global dlg
    dlg = _dlg

def new_project():
    """Utworzenie nowego projektu. Uruchamia się po naciśnięciu btn_new_prj."""
    global PATH_PRJ
    PATH_PRJ = file_dialog(is_folder=True)
    if os.path.isdir(PATH_PRJ):
        dlg.l_path_content.setText(PATH_PRJ)
        dlg.btn_adf.setEnabled(True)
        dlg.btn_bdf.setEnabled(True)

def import_adf():
    """Import .csv z danymi bazy A. Uruchamia się po naciśnięciu btn_adf."""
    global adf
    try:
        a_csv = load_csv()
    except:
        return
    if len(a_csv) == 0:
        return
    adf = ADataFrame(a_csv, dlg.imp_dlg)
    dlg.imp_dlg.tv_df.setModel(adf)
    dlg.imp_dlg.show()

def load_csv():
    """Załadowanie zawartości csv do pandas dataframe'u."""
    df_path = file_dialog(dir=PATH_PRJ, fmt='csv')
    try:
        df = pd.read_csv(df_path, error_bad_lines=False, encoding="windows 1250", delimiter=";")
    except:
        print("Błąd wczytania pliku csv.")
        return
    df.columns = ['ID', 'NAZWA', 'X', 'Y', 'Z', 'H', 'ROK', 'SKAN', 'TRANS']
    return df

def show_all():
    adf.show_all()

def show_idna():
    adf.show_idna()

def show_idnu():
    adf.show_idnu()

def show_xynv():
    adf.show_xynv()

def show_valid():
    adf.show_valid()

def file_dialog(dir='', for_open=True, fmt='', is_folder=False):
    """Dialog z eksploratorem Windows. Otwieranie/tworzenie folderów i plików."""
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    options |= QFileDialog.DontUseCustomDirectoryIcons
    dialog = QFileDialog()
    dialog.setOptions(options)
    dialog.setFilter(dialog.filter() | QDir.Hidden)
    if is_folder:  # Otwieranie folderu
        dialog.setFileMode(QFileDialog.DirectoryOnly)
    else:  # Otwieranie pliku
        dialog.setFileMode(QFileDialog.AnyFile)
    # Otwieranie / zapisywanie:
    dialog.setAcceptMode(QFileDialog.AcceptOpen) if for_open else dialog.setAcceptMode(QFileDialog.AcceptSave)
    # Ustawienie filtrowania rozszerzeń plików:
    if fmt != '' and not is_folder:
        dialog.setDefaultSuffix(fmt)
        dialog.setNameFilters([f'{fmt} (*.{fmt})'])
    # Ścieżka startowa:
    if dir != '':
        dialog.setDirectory(str(dir))
    else:
        dialog.setDirectory(str(os.environ["HOMEPATH"]))
    # Przekazanie ścieżki folderu/pliku:
    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]
        return path
    else:
        return ''
