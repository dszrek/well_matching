#!/usr/bin/python
import os

from PyQt5.QtWidgets import QFileDialog, QDialog

dlg = None

def dlg_main(_dlg):
    """Przekazanie referencji interfejsu dockwidget'u do zmiennej globalnej."""
    global dlg
    dlg = _dlg

def new_project():
    """Utworzenie nowego projektu."""
    path = create_prj_folder()
    if os.path.isdir(path):
        dlg.l_path_content.setText(path)
        dlg.btn_adf.setEnabled(True)
        dlg.btn_bdf.setEnabled(True)
    # folder = str(QFileDialog.getExistingDirectory(None, "Select Directory"))

def create_prj_folder():
    """Utworzenie folderu na dysku dla nowego projektu."""
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.DirectoryOnly)
    dialog.setAcceptMode(QFileDialog.AcceptOpen)
    dialog.setDirectory(os.environ["HOMEPATH"])
    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]  # returns a list
        return path
    else:
        return ''
