#!/usr/bin/python
import pandas as pd

from qgis.PyQt.QtCore import Qt, QAbstractTableModel, pyqtProperty, pyqtSlot, QVariant, QModelIndex


class DataFrameModel(QAbstractTableModel):
    """Podstawowy model tabeli zasilany przez pandas dataframe."""
    DtypeRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @pyqtSlot(int, Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype
        try:
            val = self._dataframe.iloc[row][col]
        except:
            print(self._dataframe)
            print(f"self._dataframe.shape, row: {row}, col: {col}")
            return QVariant()
        if role == Qt.DisplayRole:
            # Get the raw value
            if isinstance(val, float) and (index.column() == 2 or index.column() == 3):
                return "%.2f" % val
            if isinstance(val, float) and (index.column() == 4 or index.column() == 5):
                return "%.1f" % val
            if isinstance(val, float) & index.column() == 6:
                return "%.0f" % val
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()

    def roleNames(self):
        roles = {
            Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class ADataFrame(DataFrameModel):
    """Subklasa DataFrameModel obsługująca dane ze zbioru A."""
    def __init__(self, df, dlg):
        super().__init__(df)
        self.dlg = dlg  # Referencja do ui
        self.tv = dlg.tv_df  # Referencja do tableview
        # Wszystkie rekordy:
        self.all = df  # Dataframe
        self.all_cnt = len(self.all)  # Suma rekordów
        # Rekordy z pustym id:
        self.idna = df[df['ID'].isna()]
        self.idna_cnt = int()
        # Rekordy z nieunikalnymi id:
        self.idnu = df[df['ID'].duplicated(keep=False)]
        self.idnu_cnt = int()
        # Rekordy z błędną lokalizacją:
        self.xynv = None
        self.xynv_cnt = int()
        # Prawidłowe rekordy:
        self.valid = None
        self.valid_cnt = int()

        self.tv_format()
        self.init_validation()
        self.show_all()

    def __setattr__(self, attr, val):
        """Przechwycenie zmiany atrybutu."""
        if attr == "all_cnt":
            b_txt = f"Wszystkie \n \n ({val})"
            self.btn_update(self.dlg.btn_flt_all, b_txt, val)
        if attr == "idna_cnt":
            b_txt = f"Brak ID \n \n ({val})"
            self.btn_update(self.dlg.btn_flt_idna, b_txt, val)
        if attr == "idnu_cnt":
            b_txt = f"Nieunikalne ID \n \n ({val})"
            self.btn_update(self.dlg.btn_flt_idnu, b_txt, val)
        if attr == "xynv_cnt":
            b_txt = f"Błędna lokalizacja \n \n ({val})"
            self.btn_update(self.dlg.btn_flt_xynv, b_txt, val)
        if attr == "valid_cnt":
            b_txt = f"Poprawne \n \n ({val})"
            self.btn_update(self.dlg.btn_flt_valid, b_txt, val)
        super().__setattr__(attr, val)

    def btn_update(self, btn, txt, val):
        """Aktualizacja ustawień przycisku filtrującego."""
        is_enabled = True if val > 0 else False
        btn.setText(txt)
        btn.setEnabled(is_enabled)

    def show_all(self):
        """Wyświetlenie w tableview wszystkich rekordów z dataframe'a."""
        self.setDataFrame(self.all)

    def show_idna(self):
        """Wyświetlenie w tableview rekordów z pustym id."""
        self.setDataFrame(self.idna)

    def show_idnu(self):
        """Wyświetlenie w tableview rekordów z nieunikalnymi id."""
        self.setDataFrame(self.idnu)

    def show_xynv(self):
        """Wyświetlenie w tableview rekordów z pustym X i/lub Y."""
        self.setDataFrame(self.xynv)

    def show_valid(self):
        """Wyświetlenie w tableview poprawnych rekordów."""
        self.setDataFrame(self.valid)

    def tv_format(self):
        """Formatowanie kolumn tableview'u."""
        self.tv.setColumnWidth(0, 100)
        self.tv.setColumnWidth(1, 270)
        self.tv.setColumnWidth(2, 60)
        self.tv.setColumnWidth(3, 60)
        self.tv.setColumnWidth(4, 50)
        self.tv.setColumnWidth(5, 50)
        self.tv.setColumnWidth(6, 50)
        self.tv.setColumnWidth(7, 50)
        self.tv.setColumnWidth(8, 50)
        self.tv.horizontalHeader().setMinimumSectionSize(1)

    def init_validation(self):
        """Wykrycie błędów związanych z id i współrzędnymi otworów. Selekcja prawidłowych rekordów."""
        idx_nv = pd.DataFrame(columns=['idx'])  # Pusty dataframe do wrzucania indeksów błędnych rekordów
        idx_nv = idx_nv.append(pd.DataFrame(self.idna.rename_axis('idx').reset_index()['idx']), ignore_index=True)
        self.idna = self.idna.reset_index(drop=True)
        self.idna_cnt = len(self.idna)
        idx_nv = idx_nv.append(pd.DataFrame(self.idnu.rename_axis('idx').reset_index()['idx']), ignore_index=True)
        self.idnu = self.idnu.reset_index(drop=True)
        self.idnu_cnt = len(self.idnu)
        bad_x = self.all['X'].isna() | (self.all['X'] < 170000.0) | (self.all['X'] > 870000.0)
        bad_y = self.all['Y'].isna() | (self.all['Y'] < 140000.0) | (self.all['Y'] > 890000.0)
        self.xynv = self.all[ bad_x | bad_y]
        idx_nv = idx_nv.append(pd.DataFrame(self.xynv.rename_axis('idx').reset_index()['idx']), ignore_index=True)
        self.xynv = self.xynv.reset_index(drop=True)
        self.xynv_cnt = len(self.xynv)
        idx_nv.drop_duplicates(keep='first', inplace=True, ignore_index=True)
        self.valid = self.all[~self.all.reset_index().index.isin(idx_nv['idx'])]
        self.valid = self.valid.reset_index(drop=True)
        self.valid_cnt = len(self.valid)
