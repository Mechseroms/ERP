from PyQt5.QtWidgets import (QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QMdiArea, 
                             QMenuBar, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, QLabel, QToolBar, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, 
                             QMessageBox, QLineEdit, QStatusBar, QPushButton, QTextEdit)
import database, json, helpers, datetime
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QBrush, QColor
from subwindows import vendor_window
from subwindows import receipts_window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.window_properties = {}
        
        self.menu_bar: QMenuBar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("&File")
        self.purchasing_window = self.menu_bar.addMenu("&Purchasing")
        self.window_menu = self.menu_bar.addMenu("&Window")

        self.receipts_window_action: QAction = QAction()
        self.receipts_window_action.setText("Receipts")
        self.window_properties["receipt_window"] = {"active": False}
        self.purchasing_window.addAction(self.receipts_window_action)
        self.receipts_window_action.triggered.connect(self.spawn_receipts_window)

        self.vendor_window_action: QAction = QAction()
        self.vendor_window_action.setText("Vendors")
        self.window_properties["vendor_window"] = {"active": False}
        self.purchasing_window.addAction(self.vendor_window_action)
        self.vendor_window_action.triggered.connect(self.spawn_vendor_window)
        
        self.exit_app: QAction = QAction()
        self.exit_app.setText("&Exit")
        self.file_menu.addAction(self.exit_app)

    def spawn_receipts_window(self):
        if "receipt_window" in self.window_properties.keys() and not self.window_properties["receipt_window"]["active"]:
            self.receipt_window = receipts_window.ReceiptsWindow()
            self.receipt_window.closed.connect(self.despawn_window)
            self.window_properties["receipt_window"] = {"active": True}
            self.mdi_area.addSubWindow(self.receipt_window)
            self.receipt_window.show()

    def spawn_vendor_window(self):
        if "vendor_window" in self.window_properties.keys() and not self.window_properties["vendor_window"]["active"]:
            self.vendor_window = vendor_window.VendorWindow()
            self.vendor_window.closed.connect(self.despawn_window)
            self.window_properties["vendor_window"] = {"active": True}
            self.mdi_area.addSubWindow(self.vendor_window)
            self.vendor_window.show()

    def despawn_window(self, window_name: str) -> None:
        self.window_properties[window_name]["active"] = False


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()