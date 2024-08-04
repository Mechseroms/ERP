import PyQt5
import PyQt5.Qt
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt
import PyQt5.QtGui
from PyQt5.QtWidgets import (QWidget, QMainWindow, QApplication, QPushButton, 
                             QGridLayout, QTabWidget, QTreeWidget, QComboBox, 
                             QLineEdit, QVBoxLayout, QSpacerItem, QSizePolicy, 
                             QCalendarWidget, QDialog, QTreeWidgetItem, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QMessageBox, QMdiSubWindow, QStatusBar)

from helpers import random_tag

class STRWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.table_widget = QWidget()

        self.barcodes_table: QTableWidget = QTableWidget(self.table_widget)
        self.barcodes_table.setColumnCount(5)
        self.barcodes_table.setAlternatingRowColors(True)
        self.barcodes_table.setHorizontalHeaderLabels(["Data Type", "Barcode", "Name", "Qty", "Data"])   
        self.barcodes_table.resize(500, 200)
        
        self.horizontal_layout: QHBoxLayout = QHBoxLayout()

        self.vertical_layout: QVBoxLayout = QVBoxLayout()
        self.second_level_items: QWidget = QWidget()
        self.second_level_items.setMaximumHeight(55)

        self.top_level_items: QWidget = QWidget()
        self.top_level_items.setMaximumWidth(200)
        # button to open a receipt
        self.open_new_reciept: QPushButton = QPushButton(self.top_level_items)
        self.open_new_reciept.setGeometry(5, 5, 190, 45)
        self.open_new_reciept.setText(f"Open New Reciept")
        self.open_new_reciept.clicked.connect(self.open_receipt)
        # open PLU SHELF
        self.open_plu_shelf: QPushButton = QPushButton(self.top_level_items)
        self.open_plu_shelf.setGeometry(5, 55, 190, 45)
        self.open_plu_shelf.setText(f"Add from PLU Shelf")
        self.open_plu_shelf.setDisabled(True)
        # scan location
        self.scan_input = QLineEdit(self.top_level_items)
        self.scan_input.setGeometry(5, 135, 190, 40)
        self.scan_input.setPlaceholderText("Scan Barcode here...")
        self.scan_input.setDisabled(True)
        self.scan_input.textChanged.connect(self.barcode_scanned)
        # location for receipt unique id to auto populate
        self.receipt_id_input = QLineEdit(self.second_level_items)
        self.receipt_id_input.setGeometry(5, 5, 200, 45)
        self.receipt_id_input.setDisabled(True)
        # button to submit receipt
        self.submit_receipt_button: QPushButton = QPushButton(self.top_level_items)
        self.submit_receipt_button.setGeometry(5, 200, 190, 45)
        self.submit_receipt_button.setText(f"Submit Receipt")
        self.submit_receipt_button.setDisabled(True)
        self.submit_receipt_button.clicked.connect(self.submit_receipt)

        self.add_item_button: QPushButton = QPushButton(self.top_level_items)
        self.add_item_button.setHidden(True)
        self.add_item_button.clicked.connect(self.add_item)

        self.dispose_of_receipt: QPushButton = QPushButton(self.second_level_items)
        self.dispose_of_receipt.setGeometry(210, 5, 200, 45)
        self.dispose_of_receipt.setText(f"Dispose Receipt")
        self.dispose_of_receipt.setDisabled(True)
        self.dispose_of_receipt.clicked.connect(self.dispose_receipt)

        self.horizontal_layout.addWidget(self.top_level_items)
        self.horizontal_layout.addLayout(self.vertical_layout)
        
        self.vertical_layout.addWidget(self.second_level_items)
        self.vertical_layout.addWidget(self.table_widget)
        
        self.setLayout(self.horizontal_layout)

        self.receipt_open = False
        self.receipt_id = ""
        self.barcodes_table.cellChanged.connect(self.cell_changed)

        self.barcodes = {}

    def open_receipt(self):
        if self.receipt_open:
            return

        self.receipt_open = True
        self.receipt_id = f"PR-{random_tag(8)}"
        self.receipt_id_input.setText(self.receipt_id)

        self.open_plu_shelf.setDisabled(False)
        self.scan_input.setDisabled(False)
        self.submit_receipt_button.setDisabled(False)
        self.dispose_of_receipt.setDisabled(False)
        self.open_new_reciept.setDisabled(True)
        self.barcodes_table.clearContents()
        self.barcodes_table.setRowCount(0)

        self.scan_input.setFocus()

    def dispose_receipt(self):
        if not self.receipt_open:
            return
        
        self.receipt_open = False
        self.receipt_id = ""
        self.receipt_id_input.setText(self.receipt_id)
        self.barcodes = {}
        
        self.open_plu_shelf.setDisabled(True)
        self.scan_input.setDisabled(True)
        self.submit_receipt_button.setDisabled(True)
        self.dispose_of_receipt.setDisabled(True)
        self.open_new_reciept.setDisabled(False)
        self.barcodes_table.clearContents()
        self.barcodes_table.setRowCount(0)


class ReceiptsWindow(QMdiSubWindow):
    closed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.status_bar: QStatusBar = QStatusBar()