#!/usr/bin/python
import pandas as pd

from qgis.PyQt.QtCore import Qt, QAbstractTableModel, pyqtSignal, pyqtProperty, pyqtSlot, QVariant, QModelIndex


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

    flt_changed = pyqtSignal(str)
    param_changed = pyqtSignal(str)

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
        # Przetworzone rekordy:
        self.ready = None
        # Indeksy:
        self.df_in = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.df_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.idx_in = IdxDataFrame(self.df_in, self.dlg.tv_idx_in, self.dlg)
        self.idx_out = IdxDataFrame(self.df_out, self.dlg.tv_idx_out, self.dlg)
        # Dataframe'y parametrów:
        self.z_in = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.z_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.h_in = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.h_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.r_in = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.r_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])

        self.params = [
            {'param' : 'Z', 'df_in' : self.z_in, 'df_out' : self.z_out},
            {'param' : 'H', 'df_in' : self.h_in, 'df_out' : self.h_out},
            {'param' : 'ROK', 'df_in' : self.r_in, 'df_out' : self.r_out}
            ]

        self.init_validation()  # Walidacja rekordów
        self.param_indexing()  # Indeksacja parametrów
        self.flt_changed.connect(self.flt_change)
        self.flt = "valid"  # Ustawienie aktywnego filtru
        self.param_changed.connect(self.param_change)
        self.old_param = ""
        self.param = "ROK"  # Ustawienie aktywnego parametru

    def __setattr__(self, attr, val):
        """Przechwycenie zmiany atrybutu."""
        if attr == "flt":
            self.flt_changed.emit(val)
        if attr == "param":
            self.param_changed.emit(val)
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
            b_txt = f"Przetworzone \n \n ({val})"
            self.btn_update(self.dlg.btn_flt_ready, b_txt, val)
        super().__setattr__(attr, val)

    def set_flt(self, _flt):
        """Ustawienie nazwy filtru rekordów."""
        self.flt = _flt

    def flt_change(self, val):
        """Zmiana fitru danych."""
        btns = {'all' : self.dlg.btn_flt_all,
                'idna' : self.dlg.btn_flt_idna,
                'idnu' : self.dlg.btn_flt_idnu,
                'xynv' : self.dlg.btn_flt_xynv,
                'valid' : self.dlg.btn_flt_valid,
                'ready' : self.dlg.btn_flt_ready}
        self.btns_update(btns[val])

    def btns_update(self, _btn):
        """Aktualizacja stanu przycisków filtrujących."""
        btns = {self.dlg.btn_flt_all : self.all,
                self.dlg.btn_flt_idna : self.idna,
                self.dlg.btn_flt_idnu : self.idnu,
                self.dlg.btn_flt_xynv : self.xynv,
                self.dlg.btn_flt_valid : self.valid,
                self.dlg.btn_flt_ready : self.ready}
        for btn, df in btns.items():
            if btn == _btn:
                btn.setChecked(True)
                self.setDataFrame(df)
            else:
                btn.setChecked(False)

    def param_indexing(self):
        """Indeksacja parametrów."""
        for dicts in self.params:
            for key, value in dicts.items():
                if key == 'param':
                    param = value
                elif key == 'df_in':
                    df_in = value
                elif key == 'df_out':
                    df_out = value
            idxs = pd.DataFrame(self.valid[param].value_counts())
            idxs.reset_index(inplace=True)
            idxs = idxs.rename(columns = {'index' : 'WARTOŚĆ', param : 'ILOŚĆ'})
            idxs = idxs.sort_values(by='WARTOŚĆ').reset_index(drop=True)
            dicts['df_in'] = idxs

    def param_change(self, val):
        """Zmiana aktywnego parametru."""
        for dicts in self.params:
            for key, value in dicts.items():
                # Zapisanie zmian w parametrze, który przestaje być aktywny:
                if self.old_param and key == 'param' and value == self.old_param:
                    dicts['df_in'] = self.df_in
                    dicts['df_out'] = self.df_out
                # Wyszukanie dataframe'ów nowego aktywnego parametru:
                if key == 'param' and value == val:
                    new_in = dicts['df_in']
                    new_out = dicts['df_out']
        # Zmiana aktualnych dataframe'ów:
        self.df_in = new_in
        self.df_out = new_out
        self.idx_in.setDataFrame(self.df_in)
        self.idx_out.setDataFrame(self.df_out)
        self.old_param = val
        self.dlg.lab_act_param.setText(val)

    def btn_update(self, btn, txt, val):
        """Aktualizacja ustawień przycisku filtrującego."""
        is_enabled = True if val > 0 else False
        btn.setText(txt)
        btn.setEnabled(is_enabled)

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

    def index_move(self, direction):
        """Przeniesienie rekordu indeksu z tabeli indeksów ustalonych do odrzuconych lub na odwrót."""
        if direction == "down":
            _from = self.idx_in
            df_from = self.df_in
            _to = self.idx_out
            df_to = self.df_out
        elif direction == "up":
            _from = self.idx_out
            df_from = self.df_out
            _to = self.idx_in
            df_to = self.df_in
        idx_row = _from.sel_tv.currentIndex().row()
        if idx_row < 0:  # Brak zaznaczonego wiersza
            return
        sel_row = df_from[df_from.index == idx_row]
        df_to = df_to.append(sel_row, ignore_index=True)
        df_to = df_to.sort_values(by='WARTOŚĆ').reset_index(drop=True)
        df_from.drop(sel_row.index, inplace=True)
        df_from = df_from.reset_index(drop=True)
        self.df_in = df_from if direction == "down" else df_to
        self.df_out = df_to if direction == "down" else df_from
        _from.setDataFrame(df_from)
        _to.setDataFrame(df_to)

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
        self.ready = self.valid.copy()


class IdxDataFrame(DataFrameModel):
    """Subklasa DataFrameModel obsługująca indeksy wybranego parametru (np. Z)."""
    def __init__(self, df, tv, dlg):
        super().__init__(df)
        self.dlg = dlg  # Referencja do ui
        self.tv = tv  # Referencja do tableview
        self.tv.setModel(self)
        self.tv_format()  # Formatowanie kolumn tableview
        self.sel_tv = self.tv.selectionModel()
        self.sel_tv.selectionChanged.connect(self.show_index_records)

    def sel_idx(self):
        """Zwraca indeks zaznaczonego wiersza z tableview."""
        return self.sel_tv.currentIndex().row()

    def tv_format(self):
        """Formatowanie kolumn tableview'u."""
        self.tv.setColumnWidth(0, 70)
        self.tv.setColumnWidth(1, 50)
        self.tv.horizontalHeader().setMinimumSectionSize(1)

    def show_index_records(self):
        """Pokazanie w tv_df rekordów z parametrem równym wybranemu indeksowi."""
        self.dlg.adf.set_flt('valid')  # Przejście do filtru 'valid'
        index = self.sel_tv.currentIndex()
        value = index.sibling(index.row(), 0).data()
        df = self.dlg.adf.valid
        value = str(value) if df[self.dlg.adf.param].dtypes == 'object' else float(value)
        df = df[df[self.dlg.adf.param] == value].reset_index(drop=True)
        self.dlg.adf.setDataFrame(df)
