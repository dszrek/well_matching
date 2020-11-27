# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np

from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

from.classes import DataFrameModel

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'import_data_dialog.ui'))

class ImportDataDialog(QtWidgets.QDialog, FORM_CLASS):  # type: ignore

    flt_changed = pyqtSignal(str)
    param_changed = pyqtSignal(str)
    bmode_changed = pyqtSignal(bool)
    done_changed = pyqtSignal(bool)

    def __init__(self, df, a_b, dlg, parent=None):
        super(ImportDataDialog, self).__init__(parent)
        self.setupUi(self)
        self.dlg = dlg  # Referencja do interface'u dockwidget'a
        self.a_b = a_b  # Oznaczenie, który zbiór danych (A lub B)
        self.setWindowTitle(f"Import danych z bazy {self.a_b}" )
        # Utalenie ilości i nazw kolumn dla głównego dataframe'a:
        self.p_cnt = len(df.columns) - 4
        cols = ['ID', 'NAZWA', 'X', 'Y', 'Z', 'H', 'ROK', 'SKAN', 'TRANS']
        df.columns = cols[:self.p_cnt + 4]

        # Dataframe'y indeksów:
        self.df_in = pd.DataFrame(columns=['ORIGIN','WARTOŚĆ', 'ILOŚĆ'])
        self.df_out = pd.DataFrame(columns=['WARTOŚĆ', 'ILOŚĆ'])

        # Szerokości kolumn tableview'ów:
        tv_df_widths = [100, 270, 60, 60, 50, 50, 50, 50, 50]
        tv_idx_widths = [70, 50]

        # Utworzenie modeli dla tableview'ów:
        self.df_mdl = DataFrameModel(df=df, tv=self.tv_df, col_widths=tv_df_widths)
        self.mdl_in = DataFrameModel(df=self.df_in, tv=self.tv_idx_in, col_widths=tv_idx_widths)
        self.mdl_out = DataFrameModel(df=self.df_out, tv=self.tv_idx_out, col_widths=tv_idx_widths)

        # Podpięcie sygnałów zmiany indeksu zaznaczonego wiersza w tableview:
        self.tv_idx_in.selectionModel().selectionChanged.connect(lambda: self.show_index_records(self.tv_idx_in, self.df_in, self.mdl_in))
        self.tv_idx_out.selectionModel().selectionChanged.connect(lambda: self.show_index_records(self.tv_idx_out, self.df_out, self.mdl_out))

        # Konfiguracja przycisku OK:
        self.btn_ok = self.btnbx.button(QDialogButtonBox.Ok)
        self.btn_ok.setEnabled(False)
        self.btn_ok.clicked.connect(self.data_export)

        # Przyciski parametrów:
        all_pbtns = [self.btn_param_z,
            self.btn_param_h,
            self.btn_param_r,
            self.btn_param_s,
            self.btn_param_t]
        self.p_btns = all_pbtns[:self.p_cnt]
        for pbtn in all_pbtns[self.p_cnt:]:
            pbtn.setVisible(False)

        # Wskaźniki uzgodnienia parametrów:
        self.light = None
        all_lights = [self.light_z,
                    self.light_h,
                    self.light_r,
                    self.light_s,
                    self.light_t]
        self.lights = all_lights[:self.p_cnt]
        for light in all_lights[self.p_cnt:]:
            light.setVisible(False)

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

        # Parametry:
        all_params = [
            {'param' : 'Z', 'df_in' : self.z_in, 'df_out' : self.z_out, 'type_in' : self.type_in_z, 'type_out' : self.type_out_z, 'type_act' : self.type_act_z, 'done' : self.done_z, 'btn' : self.btn_param_z, 'light' : self.light_z},
            {'param' : 'H', 'df_in' : self.h_in, 'df_out' : self.h_out, 'type_in' : self.type_in_h, 'type_out' : self.type_out_h, 'type_act' : self.type_act_h, 'done' : self.done_h, 'btn' : self.btn_param_h, 'light' : self.light_h},
            {'param' : 'ROK', 'df_in' : self.r_in, 'df_out' : self.r_out, 'type_in' : self.type_in_r, 'type_out' : self.type_out_r, 'type_act' : self.type_act_r, 'done' : self.done_r, 'btn' : self.btn_param_r, 'light' : self.light_r},
            {'param' : 'SKAN', 'df_in' : self.s_in, 'df_out' : self.s_out, 'type_in' : self.type_in_s, 'type_out' : self.type_out_s, 'type_act' : self.type_act_s, 'done' : self.done_s, 'btn' : self.btn_param_s, 'light' : self.light_s},
            {'param' : 'TRANS', 'df_in' : self.t_in, 'df_out' : self.t_out, 'type_in' : self.type_in_t, 'type_out' : self.type_out_t, 'type_act' : self.type_act_t, 'done' : self.done_t, 'btn' : self.btn_param_t, 'light' : self.light_t}
            ]
        self.params = all_params[:self.p_cnt]

        # Typy danych:
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
        if len(self.cmb_type) == 0:
            for dtype in self.dtypes:
                for val in dtype.values():
                    self.cmb_type.addItem(val)
        self.cmb_type.currentIndexChanged.connect(self.cmb_type_change)

        self.btn_conn()  # Podłączenie funkcji do przycisków
        self.init_validation()  # Walidacja rekordów
        self.param_indexing()  # Indeksacja parametrów
        self.bmode = False  # Tryb aktywnego parametru typu boolean
        self.bmode_changed.connect(self.bmode_change)
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
            self.flt_btns_state(self.btn_flt_all, b_txt, val)
        if attr == "idna_cnt":
            b_txt = f"Brak ID \n \n ({val})"
            self.flt_btns_state(self.btn_flt_idna, b_txt, val)
        if attr == "idnu_cnt":
            b_txt = f"Nieunikalne ID \n \n ({val})"
            self.flt_btns_state(self.btn_flt_idnu, b_txt, val)
        if attr == "xynv_cnt":
            b_txt = f"Błędna lokalizacja \n \n ({val})"
            self.flt_btns_state(self.btn_flt_xynv, b_txt, val)
        if attr == "valid_cnt":
            b_txt = f"Poprawne \n \n ({val})"
            self.flt_btns_state(self.btn_flt_valid, b_txt, val)
            b_txt = f"Przetworzone \n \n ({val})"
            self.flt_btns_state(self.btn_flt_ready, b_txt, val)

    def init_validation(self):
        """
            Wykrycie błędów związanych z id i współrzędnymi otworów.
            Selekcja prawidłowych rekordów.
            Stworzenie podstawowych dataframe'ów: valid i ready.
        """
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

# =============== PARAMETRY:

    def set_param(self, _param):
        """Inicjacja zmiany aktywnego parametru."""
        self.param = _param

    def param_btns_update(self, _btn):
        """Aktualizacja stanu przycisków parametrów."""
        for btn in self.p_btns:
            btn.setChecked(True) if btn == _btn else btn.setChecked(False)

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
                    print(f"===================== nieobsługiwany typ: {dt} ===============================")
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
                    dicts['light'] = self.light
                # Wyszukanie dataframe'ów nowego aktywnego parametru:
                if key == 'param' and value == val:
                    new_in = dicts['df_in']
                    new_out = dicts['df_out']
                    new_type_in = dicts['type_in']
                    new_type_act = dicts['type_act']
                    new_type_out = dicts['type_out']
                    new_done = dicts['done']
                    new_btn = dicts['btn']
                    new_light = dicts['light']
        self.old_param = val
        self.lab_act_param.setText(val)
        self.param_btns_update(new_btn)
        # Zmiana aktualnych dataframe'ów:
        self.df_in = new_in
        self.df_out = new_out
        self.mdl_in.setDataFrame(self.df_in[['WARTOŚĆ', 'ILOŚĆ']])
        self.mdl_out.setDataFrame(self.df_out)
        # Zmiana w ustawieniach typu parametru:
        self.type_in = new_type_in
        self.type_act = new_type_act
        self.type_out = new_type_out
        self.lab_type_in.setText(self.type_desc(self.type_in))
        self.cmb_type.currentIndexChanged.disconnect(self.cmb_type_change)
        self.cmb_type.setCurrentText(self.type_desc(self.type_out))
        self.cmb_type.currentIndexChanged.connect(self.cmb_type_change)
        self.lab_type_act.setText(self.type_desc(self.type_act))
        self.bmode = True if self.type_out == "bool" else False
        self.light = new_light
        self.done = new_done

    def index_move(self, direction):
        """Przeniesienie rekordu indeksu z tabeli indeksów ustalonych do odrzuconych lub na odwrót."""
        if self.done:
            self.done = False
        if direction == "down":
            self.df_in['ILOŚĆ'] = self.df_in['ILOŚĆ'].astype('object')
            df_from = self.df_in
            mdl_from = self.mdl_in
            tv_from = self.tv_idx_in
            df_to = self.df_out
            mdl_to = self.mdl_out
            tv_to = self.tv_idx_out
        elif direction == "up":
            self.df_in['WARTOŚĆ'] = self.df_in['WARTOŚĆ'].astype('object')
            df_from = self.df_out
            mdl_from = self.mdl_out
            tv_from = self.tv_idx_out
            df_to = self.df_in
            mdl_to = self.mdl_in
            tv_to = self.tv_idx_in
        idx_row = tv_from.selectionModel().currentIndex().row()
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
        mdl_from.setDataFrame(df_from)
        mdl_to.setDataFrame(df_to)
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

# =============== FILTRY:

    def set_flt(self, _flt):
        """Inicjacja zmiany aktywnego filtru danych."""
        self.flt = _flt

    def flt_btns_update(self, _btn):
        """Aktualizacja stanu przycisków filtrujących."""
        btns = {self.btn_flt_all : self.all,
                self.btn_flt_idna : self.idna,
                self.btn_flt_idnu : self.idnu,
                self.btn_flt_xynv : self.xynv,
                self.btn_flt_valid : self.valid,
                self.btn_flt_ready : self.ready}
        for btn, df in btns.items():
            if btn == _btn:
                btn.setChecked(True)
                self.df_mdl.setDataFrame(df)
            else:
                btn.setChecked(False)

    def flt_btns_state(self, btn, txt, val):
        """Aktualizacja ustawień przycisków filtrujących."""
        is_enabled = True if val > 0 else False
        btn.setText(txt)
        btn.setEnabled(is_enabled)

    def flt_change(self, val):
        """Zmiana fitru danych."""
        btns = {'all' : self.btn_flt_all,
                'idna' : self.btn_flt_idna,
                'idnu' : self.btn_flt_idnu,
                'xynv' : self.btn_flt_xynv,
                'valid' : self.btn_flt_valid,
                'ready' : self.btn_flt_ready}
        self.flt_btns_update(btns[val])

# =============== TYPY DANYCH:

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
        self.lab_type_act.setText(self.type_desc(self.type_act))
        try:
            # Próba sortowania liczbowego:
            a = self.df_in['WARTOŚĆ'].astype(float).argsort()
            self.df_in = pd.DataFrame(self.df_in.values[a], self.df_in.index[a], self.df_in.columns).reset_index(drop=True)
        except:
            # Sortowanie tekstowe:
            a = self.df_in['WARTOŚĆ'].astype(str).argsort()
            self.df_in = pd.DataFrame(self.df_in.values[a], self.df_in.index[a], self.df_in.columns).reset_index(drop=True)
        self.mdl_in.setDataFrame(self.df_in[['WARTOŚĆ', 'ILOŚĆ']])

    def type_desc(self, _type):
        """Zwraca opis wybranego typu danych."""
        _type = str(_type)
        for dicts in self.dtypes:
            for dt, desc in dicts.items():
                if dt == _type:
                    return desc

    def type_name(self, _type):
        """Zwraca nazwę wybranego typu danych."""
        _type = str(_type)
        for dicts in self.dtypes:
            for dt, desc in dicts.items():
                if desc == _type:
                    return dt

    def type_conv(self, _type):
        """Konwertuje wybrany typ danych do istniejącego w combobox'ie."""
        _type = str(_type)
        for dicts in self.etypes:
            for dt, et in dicts.items():
                if dt == _type:
                    return et

    def cmb_type_change(self):
        """Zmiana wartości w combobox'ie act_type."""
        type_txt = self.cmb_type.currentText()
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

# =============== SYGNAŁY:

    def bmode_change(self, val):
        """Zmiana trybu aktywnego parametru typu boolean."""
        if val:
            self.lab_idx_in.setText("Wartości prawdy:")
            self.lab_idx_out.setText("Wartości fałszu:")
            self.btn_idx_in.setText("▲     PRAWDA     ▲")
            self.btn_idx_out.setText("▼        FAŁSZ       ▼")
        else:
            self.lab_idx_in.setText("Wartości prawidłowe:")
            self.lab_idx_out.setText("Wartości odrzucone:")
            self.btn_idx_in.setText("▲   PRZYWRÓĆ   ▲")
            self.btn_idx_out.setText("▼      ODRZUĆ     ▼")
        self.h_line.setVisible(not val)
        self.lab_type_act_title.setVisible(not val)
        self.lab_type_act.setVisible(not val)
        self.btn_bool.setVisible(val)

    def done_change(self, val):
        """Zmiana atrybutu 'done' aktywnego parametru."""
        if not val:
            # Skasowanie wszystkich zmian w ready:
            self.ready[self.param] = self.valid[self.param]
        self.btn_bool.setEnabled(not val)
        self.frm_color_update()
        self.btn_ok.setEnabled(True) if self.is_all_done() else self.btn_ok.setEnabled(False)

    def is_all_done(self):
        """Zwraca, czy wszystkie parametry zostały ustalone."""
        for dicts in self.params:
            act = False
            for key, value in dicts.items():
                if key == 'param' and value == self.param:
                    act = True
                if key == 'done':
                    done = value
            if act:
                continue
            if not done:
                return False
        if not self.done:
            return False
        return True

    def show_index_records(self, _tv, _df, _mdl):
        """Pokazanie w tv_df rekordów z parametrem równym wybranemu indeksowi."""
        sel_tv = _tv.selectionModel()
        self.set_flt('valid')  # Przejście do filtru 'valid'
        index = sel_tv.currentIndex()
        value = index.sibling(index.row(), 0).data()
        if _tv == self.tv_idx_in:  # Wartości prawidłowe
            s_df = self.df_in
            value = float(value) if self.type_act == 'float64' or self.type_act == 'Int64' else str(value)
            value = s_df[s_df['WARTOŚĆ'] == value]['ORIGIN'].values[0]
        df = self.valid
        value = str(value) if df[self.param].dtypes == 'object' else float(value)
        df = df[df[self.param] == value].reset_index(drop=True)
        self.df_mdl.setDataFrame(df)

    def btn_conn(self):
        """Podłączenie funkcji do przycisków."""
        # Filtry:
        self.btn_flt_all.clicked.connect(lambda: self.set_flt('all'))
        self.btn_flt_idna.clicked.connect(lambda: self.set_flt('idna'))
        self.btn_flt_idnu.clicked.connect(lambda: self.set_flt('idnu'))
        self.btn_flt_xynv.clicked.connect(lambda: self.set_flt('xynv'))
        self.btn_flt_valid.clicked.connect(lambda: self.set_flt('valid'))
        self.btn_flt_ready.clicked.connect(lambda: self.set_flt('ready'))
        # Parametry:
        self.btn_param_z.clicked.connect(lambda: self.set_param('Z'))
        self.btn_param_h.clicked.connect(lambda: self.set_param('H'))
        self.btn_param_r.clicked.connect(lambda: self.set_param('ROK'))
        self.btn_param_s.clicked.connect(lambda: self.set_param('SKAN'))
        self.btn_param_t.clicked.connect(lambda: self.set_param('TRANS'))
        # Indeksacja:
        self.btn_idx_out.pressed.connect(lambda: self.index_move('down'))
        self.btn_idx_in.pressed.connect(lambda: self.index_move('up'))
        # Zatwierdzenie wartości typu boolean:
        self.btn_bool.pressed.connect(self.ready_set_bool)

    def frm_color_update(self):
        """Zarządzanie kolorem ramki typów."""
        frm_red = """QFrame #frm_param_type {
                border-radius: 4px;
                border: 1px solid white;
                background-color: rgb(248,173,173)
            }"""
        frm_green = """QFrame #frm_param_type {
                border-radius: 4px;
                border: 1px solid white;
                background-color: rgb(198,224,180)
            }"""
        led_red = """QFrame {
                border-radius: 4px;
                border: 1px solid grey;
                background-color: rgb(248,173,173)
            }"""
        led_green = """QFrame {
                border-radius: 4px;
                border: 1px solid grey;
                background-color: rgb(198,224,180)
            }"""
        self.frm_param_type.setStyleSheet(frm_green) if self.done else self.frm_param_type.setStyleSheet(frm_red)
        self.light.setStyleSheet(led_green) if self.done else self.light.setStyleSheet(led_red)

    def data_export(self):
        """Zapis danych na dysku i ich załadowanie do dockwidget'a."""
        path = self.dlg.lab_path_content.text()
        if self.a_b == "A":  # Zbiór danych A
            self.ready.to_csv(f"{path}{os.path.sep}adf.csv", index=False, encoding="cp1250", sep=";")
            self.dlg.load_adf(self.ready)
        elif self.a_b == "B":  # Zbiór danych B
            name_dfs = {'Z' : 'zdf', 'H' : 'hdf', 'ROK' : 'rdf'}
            in_params = ['Z', 'H', 'ROK']
            in_params.remove(self.param)
            exp_dfs = []
            for p in in_params:
                exp_dfs.append([p, self.df_pick(p)])
            exp_dfs.append([self.param, self.df_in[['WARTOŚĆ', 'ILOŚĆ']]])
            for df in exp_dfs:
                for key, value in name_dfs.items():
                    if df[0] == key:
                        df[1].to_csv(f"{path}{os.path.sep}{value}.csv", index=False, encoding="cp1250", sep=";")
            self.dlg.load_idf(exp_dfs)
            self.ready.to_csv(f"{path}{os.path.sep}bdf.csv", index=False, encoding="cp1250", sep=";")
            self.dlg.load_bdf(self.ready)

    def df_pick(self, val):
        """Zwraca dataframe 'self.[param]_in' po podaniu parametru."""
        for dicts in self.params:
            for key, value in dicts.items():
                if key == 'param' and value == val:
                    return dicts['df_in'][['WARTOŚĆ', 'ILOŚĆ']]