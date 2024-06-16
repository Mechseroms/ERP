from PyQt5.QtWidgets import (QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QMdiArea, 
                             QMenuBar, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, QLabel, QToolBar, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, 
                             QMessageBox, QLineEdit, QTextEdit, QDialog, QTreeWidget, QTreeWidgetItem)
import database, json, helpers, datetime
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont

class ClickableTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, data):
        super().__init__()
        self.data = data

class VendorSelectDialog(QDialog):
    def __init__(self, parent, current_vendor_id) -> None:
        super().__init__(parent)
        self.current_vendor_id = current_vendor_id
        self.vendor_tree: QTreeWidget = QTreeWidget(self)
        self.vendor_tree.setGeometry(5, 5, 400, 200)
        self.vendor_tree.setHeaderLabels(["", "Vendor Name", "Vendor Address", "Vendor Phone Number"])
        self.vendor_tree.setTextElideMode(Qt.ElideRight)
        self.vendor_tree.setColumnWidth(0, 30)
        self.vendor_tree.setColumnWidth(1, 100)
        self.vendor_tree.itemDoubleClicked.connect(self.new_selected)

        self.selected_id = None
        self.vendors = None
        self.load_data()
        self.setWindowTitle("Select Vendor...")

    def load_data(self):
        self.vendors = database.fetch_vendors()
        self.refresh_ui()

    def closeEvent(self, event):
        self.reject()
        super().closeEvent(event)

    def new_selected(self, value):
        self.selected_id = value.data
        self.accept()
        
    def refresh_ui(self):
        if not self.vendors:
            return
        
        for vendor in self.vendors:
            address: str = vendor[2]
            item = ClickableTreeWidgetItem(data=vendor[0])
            if vendor[0] == self.current_vendor_id:
                pixmapi = QStyle.SP_CommandLink
                icon = self.style().standardIcon(pixmapi)
                item.setIcon(0, icon)
            item.setText(1, vendor[1])
            item.setText(2, address.replace("\n", " "))
            item.setText(3, vendor[5])
            self.vendor_tree.addTopLevelItem(item)
