#!/usr/bin/python
import os

from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import QDir

dlg = None

def dlg_main(_dlg):
    """Przekazanie referencji interfejsu dockwidget'u do zmiennej globalnej."""
    global dlg
    dlg = _dlg

def new_project():
    """Utworzenie nowego projektu."""
    path = file_dialog(is_folder=True)
    if os.path.isdir(path):
        dlg.l_path_content.setText(path)
        dlg.btn_adf.setEnabled(True)
        dlg.btn_bdf.setEnabled(True)

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
