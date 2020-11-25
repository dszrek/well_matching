#!/usr/bin/python
import pandas as pd
import numpy as np

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
    bmode_changed = pyqtSignal(bool)
    done_changed = pyqtSignal(bool)

    def __init__(self, df, dlg):
        super().__init__(df)
        self.dlg = dlg  # Referencja do ui
        self.tv = dlg.tv_df  # Referencja do tableview
        self.dlg.tv_df.setModel(self)
        self.tv_format()  # Formatowanie kolumn tableview
        self.bmode = False  # Tryb aktywnego parametru typu boolean
        self.bmode_changed.connect(self.bmode_change)
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
        self.df_in = pd.DataFrame(columns=['ORIGIN','WARTOŚĆ', 'ILOŚĆ'])
        self.df_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.idx_in = IdxDataFrame(self.df_in, self.dlg.tv_idx_in, True, self.dlg)
        self.idx_out = IdxDataFrame(self.df_out, self.dlg.tv_idx_out, False, self.dlg)
        # Dataframe'y parametrów:
        self.z_in = pd.DataFrame(columns=['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ'])
        self.z_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.h_in = pd.DataFrame(columns=['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ'])
        self.h_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.r_in = pd.DataFrame(columns=['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ'])
        self.r_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.s_in = pd.DataFrame(columns=['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ'])
        self.s_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        self.t_in = pd.DataFrame(columns=['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ'])
        self.t_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])
        # Typy parametrów:
        self.type_in = ""
        self.type_act = ""
        self.type_out = ""
        self.done = False
        self.type_in_z = ""
        self.type_act_z = ""
        self.type_out_z = ""
        self.done_z = False
        self.type_in_h = ""
        self.type_act_h = ""
        self.type_out_h = ""
        self.done_h = False
        self.type_in_r = ""
        self.type_act_r = ""
        self.type_out_r = ""
        self.done_r = False
        self.type_in_s = ""
        self.type_act_s = ""
        self.type_out_s = ""
        self.done_s = False
        self.type_in_t = ""
        self.type_act_t = ""
        self.type_out_t = ""
        self.done_t = False

        self.params = [
            {'param' : 'Z', 'df_in' : self.z_in, 'df_out' : self.z_out, 'type_in' : self.type_in_z, 'type_out' : self.type_out_z, 'type_act' : self.type_act_z, 'done' : self.done_z, 'btn' : self.dlg.btn_param_z},
            {'param' : 'H', 'df_in' : self.h_in, 'df_out' : self.h_out, 'type_in' : self.type_in_h, 'type_out' : self.type_out_h, 'type_act' : self.type_act_h, 'done' : self.done_h, 'btn' : self.dlg.btn_param_h},
            {'param' : 'ROK', 'df_in' : self.r_in, 'df_out' : self.r_out, 'type_in' : self.type_in_r, 'type_out' : self.type_out_r, 'type_act' : self.type_act_r, 'done' : self.done_r, 'btn' : self.dlg.btn_param_r},
            {'param' : 'SKAN', 'df_in' : self.s_in, 'df_out' : self.s_out, 'type_in' : self.type_in_s, 'type_out' : self.type_out_s, 'type_act' : self.type_act_s, 'done' : self.done_s, 'btn' : self.dlg.btn_param_s},
            {'param' : 'TRANS', 'df_in' : self.t_in, 'df_out' : self.t_out, 'type_in' : self.type_in_t, 'type_out' : self.type_out_t, 'type_act' : self.type_act_t, 'done' : self.done_t, 'btn' : self.dlg.btn_param_t}
            ]
        self.dtypes = [
            {None : ''},
            {'object' : 'tekst'},
            {'Int64' : 'liczba całkowita'},
            {'float64' : 'liczba ułamkowa'},
            {'bool' : 'prawda/fałsz'}
            ]
        self.etypes = [
            {'int32' : 'Int64'},
            {'int64' : 'Int64'}
        ]

        # Populacja combobox'a z oczekiwanymi typami:
        if len(self.dlg.cmb_type) == 0:
            for dtype in self.dtypes:
                for val in dtype.values():
                    self.dlg.cmb_type.addItem(val)
        self.dlg.cmb_type.currentIndexChanged.connect(self.cmb_type_change)

        self.init_validation()  # Walidacja rekordów
        self.param_indexing()  # Indeksacja parametrów
        self.flt_changed.connect(self.flt_change)
        self.flt = "valid"  # Ustawienie aktywnego filtru
        self.param_changed.connect(self.param_change)
        self.old_param = ""
        self.param = "Z"  # Ustawienie aktywnego parametru
        self.done_changed.connect(self.done_change)

    def __setattr__(self, attr, val):
        """Przechwycenie zmiany atrybutu."""
        super().__setattr__(attr, val)
        if attr == "done":
            self.done_changed.emit(val)
        if attr == "bmode":
            self.bmode_changed.emit(val)
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

    def set_flt(self, _flt):
        """Ustawienie nazwy filtru rekordów."""
        self.flt = _flt

    def set_param(self, _param):
        """Ustawienie aktywnego parametru."""
        self.param = _param

    def done_change(self, val):
        """Zmiana atrybutu 'done' aktywnego parametru."""
        if not val:
            # Skasowanie wszystkich zmian w ready:
            self.ready[self.param] = self.valid[self.param]
        self.dlg.btn_bool.setEnabled(not val)
        self.frm_color_update()

    def bmode_change(self, val):
        """Zmiana trybu aktywnego parametru typu boolean."""
        if val:
            self.dlg.lab_idx_in.setText("Wartości prawdy:")
            self.dlg.lab_idx_out.setText("Wartości fałszu:")
            self.dlg.btn_idx_in.setText("▲     PRAWDA     ▲")
            self.dlg.btn_idx_out.setText("▼        FAŁSZ       ▼")
        else:
            self.dlg.lab_idx_in.setText("Wartości prawidłowe:")
            self.dlg.lab_idx_out.setText("Wartości odrzucone:")
            self.dlg.btn_idx_in.setText("▲   PRZYWRÓĆ   ▲")
            self.dlg.btn_idx_out.setText("▼      ODRZUĆ     ▼")
        self.dlg.h_line.setVisible(not val)
        self.dlg.lab_type_act_title.setVisible(not val)
        self.dlg.lab_type_act.setVisible(not val)
        self.dlg.btn_bool.setVisible(val)

    def flt_change(self, val):
        """Zmiana fitru danych."""
        btns = {'all' : self.dlg.btn_flt_all,
                'idna' : self.dlg.btn_flt_idna,
                'idnu' : self.dlg.btn_flt_idnu,
                'xynv' : self.dlg.btn_flt_xynv,
                'valid' : self.dlg.btn_flt_valid,
                'ready' : self.dlg.btn_flt_ready}
        self.flt_btns_update(btns[val])

    def flt_btns_update(self, _btn):
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
                elif key == 'type_in':
                    type_in = value
                elif key == 'type_act':
                    type_act = value
            # Utworzenie dataframe z unikalnymi wartościami parametru:
            idxs = pd.DataFrame(self.valid[param].value_counts())
            idxs.reset_index(inplace=True)
            idxs = idxs.rename(columns = {'index' : 'WARTOŚĆ', param : 'ILOŚĆ'})
            idxs['ORIGIN'] = idxs['WARTOŚĆ']
            idxs = idxs[['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ']]
            idxs = idxs.sort_values(by='WARTOŚĆ').reset_index(drop=True)
            dicts['df_in'] = idxs
            # Zapisanie typu parametru:
            dt = self.valid[param].dtypes
            dt_chk = self.type_desc(dt)
            if not dt_chk:
                et = self.type_conv(dt)
                if et:
                    dt = et
                else:
                    print(f"=====================x-type: {dt} ===============================")
            dicts['type_in'] = dt
            dicts['type_act'] = dt

    def param_change(self, val):
        """Zmiana aktywnego parametru."""
        for dicts in self.params:
            for key, value in dicts.items():
                # Zapisanie zmian w parametrze, który przestaje być aktywny:
                if self.old_param and key == 'param' and value == self.old_param:
                    dicts['df_in'] = self.df_in
                    dicts['df_out'] = self.df_out
                    dicts['type_in'] = self.type_in
                    dicts['type_act'] = self.type_act
                    dicts['type_out'] = self.type_out
                    dicts['done'] = self.done
                # Wyszukanie dataframe'ów nowego aktywnego parametru:
                if key == 'param' and value == val:
                    new_in = dicts['df_in']
                    new_out = dicts['df_out']
                    new_type_in = dicts['type_in']
                    new_type_act = dicts['type_act']
                    new_type_out = dicts['type_out']
                    new_done = dicts['done']
                    new_btn = dicts['btn']
        self.old_param = val
        self.dlg.lab_act_param.setText(val)
        self.param_btns_update(new_btn)
        # Zmiana aktualnych dataframe'ów:
        self.df_in = new_in
        self.df_out = new_out
        self.idx_in.setDataFrame(self.df_in[['WARTOŚĆ', 'ILOŚĆ']])
        self.idx_out.setDataFrame(self.df_out)
        # Zmiana w ustawieniach typu parametru:
        self.type_in = new_type_in
        self.type_act = new_type_act
        self.type_out = new_type_out
        self.dlg.lab_type_in.setText(self.type_desc(self.type_in))
        self.dlg.cmb_type.currentIndexChanged.disconnect(self.cmb_type_change)
        self.dlg.cmb_type.setCurrentText(self.type_desc(self.type_out))
        self.dlg.cmb_type.currentIndexChanged.connect(self.cmb_type_change)
        self.dlg.lab_type_act.setText(self.type_desc(self.type_act))
        self.bmode = True if self.type_out == "bool" else False
        self.done = new_done

    def param_btns_update(self, _btn):
        """Aktualizacja stanu przycisków parametrów."""
        btns = [self.dlg.btn_param_z,
                self.dlg.btn_param_h,
                self.dlg.btn_param_r,
                self.dlg.btn_param_s,
                self.dlg.btn_param_t]
        for btn in btns:
            btn.setChecked(True) if btn == _btn else btn.setChecked(False)

    def btn_update(self, btn, txt, val):
        """Aktualizacja ustawień przycisku filtrującego."""
        is_enabled = True if val > 0 else False
        btn.setText(txt)
        btn.setEnabled(is_enabled)

    def type_desc(self, _type):
        """Zwraca opis wybranego dtypes."""
        _type = str(_type)
        for dicts in self.dtypes:
            for dt, desc in dicts.items():
                if dt == _type:
                    return desc

    def type_name(self, _type):
        """Zwraca nazwę wybranego dtypes."""
        _type = str(_type)
        for dicts in self.dtypes:
            for dt, desc in dicts.items():
                if desc == _type:
                    return dt

    def type_conv(self, _type):
        """Konwertuje wybrany dtypes do podstawowego."""
        _type = str(_type)
        for dicts in self.etypes:
            for dt, et in dicts.items():
                if dt == _type:
                    return et

    def cmb_type_change(self):
        """Zmiana wartości w combobox'ie act_type."""
        type_txt = self.dlg.cmb_type.currentText()
        self.type_out = self.type_name(type_txt)
        if type_txt == "":
            self.type_out = "object"
        if type_txt == "prawda/fałsz":
            self.bmode = True
            self.done = False
        else:
            self.bmode = False
            self.ready_set_nan()
            self.type_change()

    def type_change(self):
        """Próba zmiany typu kolumny w dataframe 'ready'."""
        if not self.bmode:
            self.done = True
            try:
                self.ready[self.param] = self.ready[self.param].astype('float').astype(self.type_out)
                self.df_in['WARTOŚĆ'] = self.df_in['WARTOŚĆ'].astype('float').astype(self.type_out)
            except Exception as error:
                self.done = False
                print(error)
        self.type_act = self.ready[self.param].dtypes
        self.dlg.lab_type_act.setText(self.type_desc(self.type_act))
        try:
            # Próba sortowania liczbowego:
            a = self.df_in['WARTOŚĆ'].astype(float).argsort()
            self.df_in = pd.DataFrame(self.df_in.values[a], self.df_in.index[a], self.df_in.columns).reset_index(drop=True)
        except:
            # Sortowanie tekstowe:
            a = self.df_in['WARTOŚĆ'].astype(str).argsort()
            self.df_in = pd.DataFrame(self.df_in.values[a], self.df_in.index[a], self.df_in.columns).reset_index(drop=True)
        self.idx_in.setDataFrame(self.df_in[['WARTOŚĆ', 'ILOŚĆ']])

    def frm_color_update(self):
        """Zarządzanie kolorem ramki typów."""
        ss_red = """QFrame #frm_param_type {
                border-radius: 4px;
                border: 1px solid white;
                background-color: rgb(248,173,173)
            }"""
        ss_green = """QFrame #frm_param_type {
                border-radius: 4px;
                border: 1px solid white;
                background-color: rgb(198,224,180)
            }"""

        self.dlg.frm_param_type.setStyleSheet(ss_green) if self.done else self.dlg.frm_param_type.setStyleSheet(ss_red)

    def index_move(self, direction):
        """Przeniesienie rekordu indeksu z tabeli indeksów ustalonych do odrzuconych lub na odwrót."""
        if self.done:
            self.done = False
        if direction == "down":
            self.df_in['ILOŚĆ'] = self.df_in['ILOŚĆ'].astype('object')
            _from = self.idx_in
            df_from = self.df_in
            _to = self.idx_out
            df_to = self.df_out
        elif direction == "up":
            self.df_in['WARTOŚĆ'] = self.df_in['WARTOŚĆ'].astype('object')
            _from = self.idx_out
            df_from = self.df_out
            _to = self.idx_in
            df_to = self.df_in
        idx_row = _from.sel_tv.currentIndex().row()
        if idx_row < 0:  # Brak zaznaczonego wiersza
            return
        sel_row = df_from[df_from.index == idx_row]
        if direction == "down":
            sel_row = sel_row[['ORIGIN', 'ILOŚĆ']].rename(columns = {'ORIGIN' : 'WARTOŚĆ'})
        elif direction == "up":
            sel_row['ORIGIN'] = sel_row['WARTOŚĆ']
            sel_row = sel_row[['ORIGIN', 'WARTOŚĆ', 'ILOŚĆ']]
        df_to = df_to.append(sel_row, ignore_index=True)
        if len(df_from) > 1:
            try:
                # Próba sortowania liczbowego:
                a = df_from['WARTOŚĆ'].astype(float).argsort()
                df_from = pd.DataFrame(df_from.values[a], df_from.index[a], df_from.columns).reset_index(drop=True)
            except:
                # Sortowanie tekstowe:
                a = df_from['WARTOŚĆ'].astype(str).argsort()
                df_from = pd.DataFrame(df_from.values[a], df_from.index[a], df_from.columns).reset_index(drop=True)
        if len(df_to) > 1:
            try:
                # Próba sortowania liczbowego:
                a = df_to['WARTOŚĆ'].astype(float).argsort()
                df_to = pd.DataFrame(df_to.values[a], df_to.index[a], df_to.columns).reset_index(drop=True)
            except:
                # Sortowanie tekstowe:
                a = df_to['WARTOŚĆ'].astype(str).argsort()
                df_to = pd.DataFrame(df_to.values[a], df_to.index[a], df_to.columns).reset_index(drop=True)
        df_from.drop(sel_row.index, inplace=True)
        df_from = df_from.reset_index(drop=True)
        self.df_in = df_from if direction == "down" else df_to
        self.df_out = df_to if direction == "down" else df_from
        _from.setDataFrame(df_from)
        _to.setDataFrame(df_to)
        if not self.bmode:
            self.ready_set_nan()
        self.type_change()  # Próba zmiany typu kolumny

    def ready_set_nan(self):
        """Aktualizacja wartości NaN w df_ready."""
        # Ustawienie wartości NaN w odpowiednich komórkach:
        out_vals = self.df_out['WARTOŚĆ'].tolist()
        self.ready.loc[self.ready[self.param].isin(out_vals), self.param] = np.nan

    def ready_set_bool(self):
        """Aktualizacja wartości bool w df_ready."""
        self.ready[self.param] = self.ready[self.param].astype('object')
        # Ustawienie wartości boolean w odpowiednich komórkach:
        t_vals = self.df_in['WARTOŚĆ'].tolist()
        f_vals = self.df_out['WARTOŚĆ'].tolist()
        self.ready.loc[self.ready[self.param].isin(t_vals), self.param] = True
        self.ready.loc[self.ready[self.param].isin(f_vals), self.param] = False
        self.ready[self.param].fillna(False, inplace=True)
        self.ready[self.param] = self.ready[self.param].astype('bool')
        self.done = True

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


class IdxDataFrame(DataFrameModel):
    """Subklasa DataFrameModel obsługująca indeksy wybranego parametru (np. Z)."""
    def __init__(self, df, tv, _in, dlg):
        super().__init__(df)
        self._in = _in
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
        if self._in:  # Wartości prawidłowe
            s_df = self.dlg.adf.df_in
            value = float(value) if self.dlg.adf.type_act == 'float64' or self.dlg.adf.type_act == 'Int64' else str(value)
            value = s_df[s_df['WARTOŚĆ'] == value]['ORIGIN'].values[0]
        df = self.dlg.adf.valid
        value = str(value) if df[self.dlg.adf.param].dtypes == 'object' else float(value)
        df = df[df[self.dlg.adf.param] == value].reset_index(drop=True)
        self.dlg.adf.setDataFrame(df)
