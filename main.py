#!/usr/bin/python
import os
import pandas as pd

from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import QDir

from .import_data_dialog import ImportDataDialog
from .classes import DataFrameModel


PATH_PRJ = None
dlg = None
adf = None

def dlg_main(_dlg):
    """Przekazanie referencji interfejsu dockwidget'u do zmiennej globalnej."""
    global dlg
    dlg = _dlg
    dlg.btn_new_prj.pressed.connect(new_project)
    dlg.btn_adf.pressed.connect(import_adf)
    dlg.btn_bdf.pressed.connect(import_bdf)

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
    global dlg
    try:
        a_csv = load_csv()
    except:
        return
    if a_csv is None:
        return
    dlg.impdlg = ImportDataDialog(a_csv)
    dlg.impdlg.show()

def import_bdf():
    """Import .csv z danymi bazy B. Uruchamia się po naciśnięciu btn_bdf."""
    global bdf
    try:
        b_csv = load_csv()
    except:
        return
    if b_csv is None:
        return
    dlg.impdlg = ImportDataDialog(b_csv)
    dlg.impdlg.show()

def load_csv():
    """Załadowanie zawartości csv do pandas dataframe'u."""
    df_path = file_dialog(dir=PATH_PRJ, fmt='csv')
    try:
        df = pd.read_csv(df_path, error_bad_lines=False, encoding="windows 1250", delimiter=";")
    except:
        print("Błąd wczytania pliku csv.")
        return
    return df


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
