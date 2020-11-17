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
    def __init__(self, df):
        super().__init__(df)
        # Wszystkie rekordy:
        self.all = df
        # Rekordy z pustym id:
        self.idna = df[df['ID'].isna()].reset_index(drop=True).copy()
        # Rekordy z niunikalnymi id:
        self.idnu = df[df['ID'].duplicated(keep=False)].reset_index(drop=True).copy()
        # Rekordy z błędną lokalizacją:
        bad_x = df['X'].isna() | (df['X'] < 170000.0) | (df['X'] > 870000.0)
        bad_y = df['Y'].isna() | (df['Y'] < 140000.0) | (df['Y'] > 890000.0)
        self.xynv = df[ bad_x | bad_y].reset_index(drop=True).copy()

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
