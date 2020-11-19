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
            # print(self._dataframe)
            # print(f"self._dataframe.shape, row: {row}, col: {col}")
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
        self.dlg.tv_df.setModel(self)
        self.tv_format()  # Formatowanie kolumn tableview
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

        self.init_validation()  # Walidacja rekordów
        self.btn_mgr(dlg.btn_flt_all, False)  # Pokazanie wszystkich rekordów


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

    def btn_mgr(self, _btn, is_clicked):
        """Zarządzanie przyciskami filtrującymi."""
        btns = {self.dlg.btn_flt_all : self.all,
                self.dlg.btn_flt_idna : self.idna,
                self.dlg.btn_flt_idnu : self.idnu,
                self.dlg.btn_flt_xynv : self.xynv,
                self.dlg.btn_flt_valid : self.valid}
        for btn, df in btns.items():
            if btn == _btn:
                if not is_clicked:
                    btn.setChecked(True)
                self.setDataFrame(df)
            else:
                btn.setChecked(False)

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

        # print(self.valid['Z'].dtypes)
        # self.valid['Z'] = pd.to_numeric(self.valid['Z'], errors='coerce')
        # self.valid['Z'].astype(float).applymap('{:,.2f}'.format))
        z_vals = pd.DataFrame(self.valid['Z'].value_counts())
        z_vals.reset_index(inplace=True)
        z_vals = z_vals.rename(columns = {'index' : 'Z', 'Z' : 'LICZNIK'})
        z_vals = z_vals.sort_values(by='Z').reset_index(drop=True)
        idf = IdxDataFrame(z_vals, self.dlg)


class IdxDataFrame(DataFrameModel):
    """Subklasa DataFrameModel obsługująca dane ze zbioru A."""
    def __init__(self, df, dlg):
        super().__init__(df)
        self.dlg = dlg  # Referencja do ui
        self.tv = dlg.tv_z  # Referencja do tableview
        self.tv.setModel(self)
        self.tv_format()  # Formatowanie kolumn tableview
        self.sel_tv = self.tv.selectionModel()
        self.sel_tv.selectionChanged.connect(self.show_index_records)

    def tv_format(self):
        """Formatowanie kolumn tableview'u."""
        self.tv.setColumnWidth(0, 50)
        self.tv.setColumnWidth(1, 50)
        self.tv.horizontalHeader().setMinimumSectionSize(1)

    def show_index_records(self):
        index = self.sel_tv.currentIndex()
        value = index.sibling(index.row(), 0).data()
        df = self.dlg.adf.valid
        df = df[df['Z'] == value].reset_index(drop=True)
        self.dlg.adf.setDataFrame(df)