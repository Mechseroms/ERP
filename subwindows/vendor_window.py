from PyQt5.QtWidgets import (QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QMdiArea, 
                             QMenuBar, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, QLabel, QToolBar, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, 
                             QMessageBox, QLineEdit)
import database, json, helpers
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont


class VendorWindow(QMdiSubWindow):
    def __init__(self) -> None:
        super().__init__()

        self.resize(1200, 720)
        self.setWindowTitle("Receipts")
        self.load_data()

    def load_data(self):
        print("hello")