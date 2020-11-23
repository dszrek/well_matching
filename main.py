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
    dlg.imp_dlg.adf = ADataFrame(a_csv, dlg.imp_dlg)
    # dlg.imp_dlg.tv_df.setModel(adf)
    btn_conn()
    dlg.imp_dlg.show()

def load_csv():
    """Załadowanie zawartości csv do pandas dataframe'u."""
    df_path = file_dialog(dir=PATH_PRJ, fmt='csv')
    try:
        df = pd.read_csv(df_path, error_bad_lines=False, encoding="windows 1250", delimiter=";")
    except:
        print("Błąd wczytania pliku csv.")
        return
    # df.columns = ['ID', 'NAZWA', 'X', 'Y', 'Z', 'H', 'ROK']
    df.columns = ['ID', 'NAZWA', 'X', 'Y', 'Z', 'H', 'ROK', 'SKAN', 'TRANS']
    return df

def btn_conn():
    """Podłączenie funkcji do przycisków filtrujących."""
    # Filtry:
    dlg.imp_dlg.btn_flt_all.clicked.connect(lambda: dlg.imp_dlg.adf.set_flt('all'))
    dlg.imp_dlg.btn_flt_idna.clicked.connect(lambda: dlg.imp_dlg.adf.set_flt('idna'))
    dlg.imp_dlg.btn_flt_idnu.clicked.connect(lambda: dlg.imp_dlg.adf.set_flt('idnu'))
    dlg.imp_dlg.btn_flt_xynv.clicked.connect(lambda: dlg.imp_dlg.adf.set_flt('xynv'))
    dlg.imp_dlg.btn_flt_valid.clicked.connect(lambda: dlg.imp_dlg.adf.set_flt('valid'))
    dlg.imp_dlg.btn_flt_ready.clicked.connect(lambda: dlg.imp_dlg.adf.set_flt('ready'))
    # Parametry:
    dlg.imp_dlg.btn_param_z.clicked.connect(lambda: dlg.imp_dlg.adf.set_param('Z'))
    dlg.imp_dlg.btn_param_h.clicked.connect(lambda: dlg.imp_dlg.adf.set_param('H'))
    dlg.imp_dlg.btn_param_r.clicked.connect(lambda: dlg.imp_dlg.adf.set_param('ROK'))
    # Indeksacja:
    dlg.imp_dlg.btn_idx_out.pressed.connect(lambda: dlg.imp_dlg.adf.index_move('down'))
    dlg.imp_dlg.btn_idx_in.pressed.connect(lambda: dlg.imp_dlg.adf.index_move('up'))

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
