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
    dlg.btn_open_prj.pressed.connect(open_project)
    dlg.btn_adf.pressed.connect(import_adf)
    dlg.btn_bdf.pressed.connect(import_bdf)

def new_project():
    """Utworzenie nowego projektu. Uruchamia się po naciśnięciu btn_new_prj."""
    global PATH_PRJ
    PATH_PRJ = file_dialog(is_folder=True)
    if os.path.isdir(PATH_PRJ):
        dlg.lab_path_content.setText(PATH_PRJ)
        btn_reset()

def open_project():
    """Załadowanie zapisanego projektu. Uruchamia się po naciśnięciu btn_open_prj."""
    global PATH_PRJ, dlg
    btn_reset()
    PATH_PRJ = file_dialog(is_folder=True)
    if not os.path.isdir(PATH_PRJ):
        return
    dlg.lab_path_content.setText(PATH_PRJ)
    # Próba wczytania zbioru danych A:
    f_path = f"{PATH_PRJ}{os.path.sep}adf.csv"
    f_path = f_path.replace("\\", "/")
    if os.path.isfile(f_path):
        dlg.load_adf(load_csv(f_path))
    # Próba wczytania zbioru danych B:
    idfs = idfs_load()
    if not idfs:  # Nie ma kompletu plików
        return
    f_path = f"{PATH_PRJ}{os.path.sep}bdf.csv"
    dlg.load_bdf(load_csv(f_path))
    dlg.load_idf(idfs)

def idfs_load():
    """Zwraca dataframe'y indeksów z bazy B. Pusty, jeśli nie ma kompletu plików."""
    bdfs = [['bdf', 'bdf'], ['Z', 'zdf'], ['H', 'hdf'], ['ROK', 'rdf']]
    imp_dfs = []
    for df in bdfs:
        f_path = f"{PATH_PRJ}{os.path.sep}{df[1]}.csv"
        if not os.path.isfile(f_path):
            return
        else:
            if df[0] != 'bdf':
                imp_dfs.append([df[0], load_csv(f_path)])
    return imp_dfs

def import_adf():
    """Import .csv z danymi bazy A. Uruchamia się po naciśnięciu btn_adf."""
    global dlg
    try:
        a_csv = load_csv()
    except:
        return
    if a_csv is None:
        return
    dlg.impdlg = ImportDataDialog(a_csv, 'A', dlg)
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
    dlg.impdlg = ImportDataDialog(b_csv, 'B', dlg)
    dlg.impdlg.show()

def load_csv(df_path=None):
    """Załadowanie zawartości csv do pandas dataframe'u."""
    if not df_path:
        df_path = file_dialog(dir=PATH_PRJ, fmt='csv')
    try:
        df = pd.read_csv(df_path, error_bad_lines=False, encoding="cp1250", delimiter=";")
    except Exception as error:
        print(error)
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

def btn_reset():
    """Resetuje stan przycisków importu baz."""
    dlg.btn_adf.setEnabled(True)
    dlg.btn_adf.setText("Importuj bazę A")
    dlg.btn_bdf.setEnabled(True)
    dlg.btn_bdf.setText("Importuj bazę B")
