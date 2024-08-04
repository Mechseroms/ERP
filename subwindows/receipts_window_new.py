from PyQt5.QtWidgets import (QFrame,   QHBoxLayout, QVBoxLayout, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, 
                             QLabel, QToolBar, QGroupBox, QGridLayout, QMessageBox, QLineEdit, QStatusBar, QCalendarWidget, 
                             QPushButton, QTextEdit, QTreeWidgetItem, QDialog, QTreeWidget, QComboBox)
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QFontMetrics

import database
import helpers
import datetime
import subwindows.InventoryItemSelect as inventory_select

class ClickableTreeWidgetItem(QTreeWidgetItem):
    """Created with the sole purpose of adding a data variable.

    Could just be my lack of knowledge at the moment, but this is the best way i could
    think about saving a unique id into an item to be called on later during signal calls.
    """
    def __init__(self, data: any = None) -> None:
        super().__init__()
        self.data = data

class ReceiptMainToolbar(QToolBar):
    buttonHovered = pyqtSignal(str)
    denied = pyqtSignal()
    resolve = pyqtSignal()
    deleteReceipt = pyqtSignal()
    saveReceipt = pyqtSignal()
    openFiles = pyqtSignal()
    addReceipt = pyqtSignal()
    openHelp = pyqtSignal()

    def __init__(self, title):
        super().__init__(title)

        # Add
        # Delete
        # Save
        # Resolve
        # Deny
        # help
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setStatusTip("Deletes the current selected receipt, any unsaved changes will be lost!")
        self.delete_action.hovered.connect(lambda: self.buttonHovered.emit(self.delete_action.statusTip()))
        self.delete_action.triggered.connect(self.deleteReceipt.emit)

        self.save_action = QAction("&Save", self)
        self.save_action.setStatusTip("Saves the current selected receipt.")
        self.save_action.hovered.connect(lambda: self.buttonHovered.emit(self.save_action.statusTip()))
        self.save_action.triggered.connect(self.saveReceipt.emit)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.help_action = QAction("&Help", self)
        self.help_action.setStatusTip("Opens a help document..")
        self.help_action.hovered.connect(lambda: self.buttonHovered.emit(self.help_action.statusTip()))
        self.help_action.triggered.connect(self.openHelp.emit)

        self.resolve_action = QAction("&Resolve", self)
        self.resolve_action.setStatusTip("Resolves the Selected Receipt and sets it to Resolved and transacts it into the system.")
        self.resolve_action.hovered.connect(lambda: self.buttonHovered.emit(self.resolve_action.statusTip()))
        self.resolve_action.triggered.connect(self.resolve.emit)

        # Deny
        self.deny_action = QAction("&Deny", self)
        self.deny_action.setStatusTip("Denies the Receipt and sets it to Denied; this means nothing is transacted into the Database.")
        self.deny_action.hovered.connect(lambda: self.buttonHovered.emit(self.deny_action.statusTip()))
        self.deny_action.triggered.connect(self.denied.emit)

        self.files_action = QAction("&Files", self)
        self.files_action.setStatusTip("Attach Files to the Selected Receipt!")
        self.files_action.hovered.connect(lambda: self.buttonHovered.emit(self.files_action.statusTip()))
        self.files_action.triggered.connect(self.openFiles.emit)

        self.add_receipt_action = QAction("&Add", self)
        self.add_receipt_action.setStatusTip("Open a new receipt in the Database!")
        self.add_receipt_action.hovered.connect(lambda: self.buttonHovered.emit(self.add_receipt_action.statusTip()))
        self.add_receipt_action.triggered.connect(self.addReceipt.emit)

        self.addAction(self.resolve_action)
        self.addAction(self.deny_action)
        self.addSeparator()
        self.addAction(self.add_receipt_action)
        self.addAction(self.save_action)
        self.addAction(self.delete_action)
        self.addSeparator()
        self.addAction(self.files_action)
        self.addWidget(spacer)
        self.addAction(self.help_action)

    def setStates(self, state):
        self.save_action.setDisabled(state)
        self.delete_action.setDisabled(state)
        self.resolve_action.setDisabled(state)
        self.deny_action.setDisabled(state)

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

class ItemDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.grid_layout: QGridLayout = QGridLayout()

        self.item_type = "INSERT"
        self.type_label: QLabel = QLabel()
        self.type_label.setText("type")

        self.type_input: QLineEdit = QLineEdit()
        self.type_input.setEnabled(False)

        # Barcode, label, input, lookup_button
        self.barcode_label: QLabel = QLabel()
        self.barcode_label.setText("Barcode")

        self.barcode_input: QLineEdit = QLineEdit()
        self.barcode_input.editingFinished.connect(self.check_database)
        
        self.lookup_button: QPushButton = QPushButton()
        self.lookup_button.setText("Lookup")
        self.lookup_button.clicked.connect(self.lookup_process)
        #name
        self.name_label: QLabel = QLabel()
        self.name_label.setText("Name")

        self.name_input: QLineEdit = QLineEdit()
        
        # qty
        self.qty_label: QLabel = QLabel()
        self.qty_label.setText("Qty")

        self.qty_input: QLineEdit = QLineEdit()
        
        #subtype
        self.subtype_label: QLabel = QLabel()
        self.subtype_label.setText("Subtype")

        self.subtype_input: QComboBox = QComboBox()
        self.subtype_input.addItems(["FOOD", "FOOD(PLU)", "OTHER"])
        
        #cost
        self.cost_label: QLabel = QLabel()
        self.cost_label.setText("Cost")

        self.cost_input: QLineEdit = QLineEdit()
        
        #packaging
        self.packaging_label: QLabel = QLabel()
        self.packaging_label.setText("Packaging")

        self.packaging_input: QLineEdit = QLineEdit()
        
        # expires
        self.expires_label: QLabel = QLabel()
        self.expires_label.setText("Expires")

        self.expires_input: QComboBox = QComboBox()
        self.expires_input.addItems(["No", "Yes"])
        self.expires_input.currentTextChanged.connect(self.setExpirey)
        
        # expiry date
        self.expiration_label: QLabel = QLabel()
        self.expiration_label.setText("Barcode")

        self.expiration_input: QCalendarWidget = QCalendarWidget()
        self.expiration_input.setEnabled(False)
        
        #safety stock
        self.safety_stock_label: QLabel = QLabel()
        self.safety_stock_label.setText("Safety Stock")

        self.safety_stock_input: QLineEdit = QLineEdit()
        
        self.state = "Unresolved"

        self.submit_button: QPushButton = QPushButton()
        self.submit_button.setText("Submit")
        self.submit_button.clicked.connect(self.submit_item)

        self.grid_layout.addWidget(self.type_label, 0, 0)
        self.grid_layout.addWidget(self.type_input, 0, 1)

        self.grid_layout.addWidget(self.barcode_label, 1, 0)
        self.grid_layout.addWidget(self.barcode_input, 1, 1)
        self.grid_layout.addWidget(self.lookup_button, 1, 2)

        self.grid_layout.addWidget(self.name_label, 2, 0)
        self.grid_layout.addWidget(self.name_input, 2, 1)

        self.grid_layout.addWidget(self.qty_label, 3, 0)
        self.grid_layout.addWidget(self.qty_input, 3, 1)
        
        self.grid_layout.addWidget(self.subtype_label, 4, 0)
        self.grid_layout.addWidget(self.subtype_input, 4, 1)

        self.grid_layout.addWidget(self.cost_label, 5, 0)
        self.grid_layout.addWidget(self.cost_input, 5, 1)

        self.grid_layout.addWidget(self.packaging_label, 6, 0)
        self.grid_layout.addWidget(self.packaging_input, 6, 1)

        self.grid_layout.addWidget(self.safety_stock_label, 7, 0)
        self.grid_layout.addWidget(self.safety_stock_input, 7, 1)

        self.grid_layout.addWidget(self.expires_label, 8, 0)
        self.grid_layout.addWidget(self.expires_input, 8, 1)

        self.grid_layout.addWidget(self.expiration_input, 9, 0, 1, 3)

        self.grid_layout.addWidget(self.submit_button, 10, 2)

        self.selected_id = 0

        self.setLayout(self.grid_layout)
        self.setWindowTitle("Add/Edit Item...")
    
    def check_database(self):
        success, data = helpers.check_barcode(f"{self.barcode_input.text()}")
        if success:
            self.selected_id = data["id"]
            self.setFields(
                item_type="Pantry",
                barcode=data["barcode"],
                name=data["name"],
                subtype=data["sub_type"],
                cost=data["cost"],
                packaging=data["product_quantity_unit"],
                safety_stock=data["safety_stock"],
                expires=data["expires"]
                )
        else:
            self.selected_id = 0
            self.setFields()

    def setEditMode(self, state: bool):
        self.barcode_input.setDisabled(state)
        self.lookup_button.setDisabled(state)
    def setFields(self, item_type: str = "Insert", barcode: str = "",
                  name: str = "Unknown", qty: int = 0, subtype: str = "OTHER", 
                  cost: float = 0.00, packaging: str = "Each", safety_stock: int = 0,
                  expires: str = "No"):
        


        self.type_input.setText(item_type)
        self.barcode_input.setText(barcode)
        # name
        self.name_input.setText(name)
        #qty
        self.qty_input.setText(str(qty))
        #subtype
        self.subtype_input.setCurrentText(subtype)
        #cost
        self.cost_input.setText(str(cost))
        #packaging
        self.packaging_input.setText(packaging)
        #safety_stock
        self.safety_stock_input.setText(str(safety_stock))
        #expires
        self.expires_input.setCurrentText(str(expires))

    def lookup_process(self):
        d = inventory_select.ItemSelectDialog(self)
        d.setFont(self.font())
        result = d.exec_()
        if result:
            data = database.fetch_pantry(d.selected_id)
            self.barcode_input.setText(data[1])
            self.setFields(
                item_type="Pantry",
                barcode=data[1],
                name=data[2],
                subtype=data[24],
                cost=data[15],
                packaging=data[13],
                safety_stock=data[17],
                expires=data[22]
            )

    def setExpirey(self, value):
        if value == "No":
            self.expiration_input.setEnabled(False)
        elif value == "Yes":
            self.expiration_input.setEnabled(True)

    def getFields(self):
        expiry_date = ""
        if self.expires_input.currentText() == "Yes":
            expiry_date = self.expiration_input.selectedDate().toPyDate()
        return [
            self.selected_id,
            self.type_input.text(),
            self.barcode_input.text(),
            self.name_input.text(),
            self.qty_input.text(),
            {"cost": self.cost_input.text(), 
             "expires": self.expires_input.currentText().lower(),
             "product_quantity_unit": self.packaging_input.text(),
             "safety_stock": self.safety_stock_input.text(), 
             "Expiry Date": expiry_date,
             "sub_type": self.subtype_input.currentText().upper()},
            "Unresolved"
        ]

    def submit_item(self):
        print("submitted")
        self.accept()

    def closeEvent(self, event):
        self.reject()
        super().closeEvent(event)

class ItemSelectDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.grid_layout: QGridLayout = QGridLayout()

        self.item_tree: QTreeWidget = QTreeWidget(self)
        self.item_tree.setHeaderLabels(["ID", "Status", "Date Submitted", "Submitted By"])
        self.item_tree.setAlternatingRowColors(True)
        self.item_tree.itemDoubleClicked.connect(self.new_selected)


        st = """
            QPushButton {
                background-color: #D3D3D3;
                border: none;
                border-radius: 10px;
                padding: 2px;
                color: #2F4F4F;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #DCDCDC;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """

        self.grid_layout.addWidget(self.item_tree, 0, 0, 0, 0)

        self.setLayout(self.grid_layout)
        self.setWindowTitle("Select Receipt Item...")
        self.resize(1000, 300)

        self.selected_id = 0
        self.load_data()

    def load_data(self):
        items = database.fetch_receipts() 
           
        self.item_tree.clear()
        for item in reversed(items):
            listItem = ClickableTreeWidgetItem(item[0])
            listItem.setText(0, str(item[1]))
            listItem.setText(1, str(item[3]))
            listItem.setText(2, str(item[4]))
            listItem.setText(3, str(item[5]))
            self.item_tree.addTopLevelItem(listItem)

        self.item_tree.setTextElideMode(Qt.ElideRight)
        self.item_tree.setColumnWidth(0, 200)
        self.item_tree.setColumnWidth(1, 100)
        self.item_tree.setColumnWidth(2, 100)
        self.item_tree.setColumnWidth(3, 100)
    
    def closeEvent(self, event):
        self.reject()
        super().closeEvent(event)

    def new_selected(self, value):
        self.selected_id = value.data
        self.accept()

class ReceiptVendorGroup(QGroupBox):
    vendorSelected = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.vendor_grid: QGridLayout = QGridLayout()
        self.setLayout(self.vendor_grid)

        self.vendor_name_label: QLabel = QLabel()
        self.vendor_name_label.setText("Name: ")
        font_metric = QFontMetrics(self.vendor_name_label.font())
        width = font_metric.width(self.vendor_name_label.text())
        self.vendor_name_label.setMaximumWidth(width)
        self.vendor_name_edit: QLineEdit = QLineEdit()
        self.vendor_name_edit.setReadOnly(True)
        self.vendor_name_edit.setMaximumWidth(180)
        self.vendor_select_button: QPushButton = QPushButton()
        self.vendor_select_button.setText("s")
        self.vendor_select_button.setMaximumWidth(30)
        self.vendor_select_button.clicked.connect(self.openDialog)

        self.vendor_phone_label: QLabel = QLabel()
        self.vendor_phone_label.setText("Phone: ")
        font_metric = QFontMetrics(self.vendor_phone_label.font())
        width = font_metric.width(self.vendor_phone_label.text())
        self.vendor_phone_label.setMaximumWidth(width)
        self.vendor_phone_edit: QLineEdit = QLineEdit()
        self.vendor_phone_edit.setReadOnly(True)
        self.vendor_phone_edit.setMaximumWidth(180)

        self.vendor_address_label: QLabel = QLabel()
        self.vendor_address_label.setText("Address: ")
        font_metric = QFontMetrics(self.vendor_address_label.font())
        width = font_metric.width(self.vendor_address_label.text())
        self.vendor_address_label.setMaximumWidth(width)
        self.vendor_address_edit: QTextEdit = QTextEdit()
        self.vendor_address_edit.setReadOnly(True)
        self.vendor_address_edit.setMaximumWidth(180)
        self.vendor_address_edit.setMaximumHeight(75)

        self.vendor_grid.addWidget(self.vendor_name_label, 0, 0)
        self.vendor_grid.addWidget(self.vendor_name_edit, 0, 1)
        self.vendor_grid.addWidget(self.vendor_select_button, 0, 2)

        self.vendor_grid.addWidget(self.vendor_phone_label, 1, 0)
        self.vendor_grid.addWidget(self.vendor_phone_edit, 1, 1)

        self.vendor_grid.addWidget(self.vendor_address_label, 2, 0)
        self.vendor_grid.addWidget(self.vendor_address_edit, 2, 1)

        self._vendor_id = None

    def openDialog(self):
        d = VendorSelectDialog(self, self._vendor_id)
        result = d.exec_()
        if result:
            self._vendor_id = d.selected_id
            self.vendorSelected.emit(self._vendor_id)

    def setVendorId(self, id: int):
        self._vendor_id = id

    def setStates(self, state: bool):
        self.vendor_select_button.setDisabled(state)

    def setFields(self, name, phone, address):
        self.vendor_name_edit.setText(name)
        self.vendor_phone_edit.setText(phone)
        self.vendor_address_edit.setText(address)

class ReceiptInfoGroup(QGroupBox):
    itemSelected = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()

        self.info_grid: QGridLayout = QGridLayout()
        self.setLayout(self.info_grid)

        self.receipt_id_label: QLabel = QLabel()
        self.receipt_id_label.setText("Receipt ID: ")
        font_metric = QFontMetrics(self.receipt_id_label.font())
        width = font_metric.width(self.receipt_id_label.text())
        self.receipt_id_label.setMaximumWidth(width)
        self.receipt_id_edit: QLineEdit = QLineEdit()
        self.receipt_id_edit.setReadOnly(True)
        self.receipt_id_edit.setMaximumWidth(180)

        self.receipt_select: QPushButton = QPushButton()
        self.receipt_select.setText("s")
        self.receipt_select.clicked.connect(self.lookup_process)
        self.receipt_select.setMaximumSize(60, 25)

        self.receipt_status_label: QLabel = QLabel()
        self.receipt_status_label.setText("Receipt Status: ")
        font_metric = QFontMetrics(self.receipt_status_label.font())
        width = font_metric.width(self.receipt_status_label.text())
        self.receipt_status_label.setMaximumWidth(width)
        self.receipt_status_edit: QLineEdit = QLineEdit()
        self.receipt_status_edit.setReadOnly(True)
        self.receipt_status_edit.setMaximumWidth(180)

        self.date_submitted_label: QLabel = QLabel()
        self.date_submitted_label.setText("Date Submitted: ")
        font_metric = QFontMetrics(self.date_submitted_label.font())
        width = font_metric.width(self.date_submitted_label.text())
        self.date_submitted_label.setMaximumWidth(width)
        self.date_submitted_edit: QLineEdit = QLineEdit()
        self.date_submitted_edit.setReadOnly(True)
        self.date_submitted_edit.setMaximumWidth(180)

        self.submitted_by_label: QLabel = QLabel()
        self.submitted_by_label.setText("Submitted By: ")
        font_metric = QFontMetrics(self.submitted_by_label.font())
        width = font_metric.width(self.submitted_by_label.text())
        self.submitted_by_label.setMaximumWidth(width)
        self.submitted_by_edit: QLineEdit = QLineEdit()
        self.submitted_by_edit.setReadOnly(True)
        self.submitted_by_edit.setMaximumWidth(180)

        self.receipt_length_label: QLabel = QLabel()
        self.receipt_length_label.setText("Receipt Length: ")
        font_metric = QFontMetrics(self.receipt_length_label.font())
        width = font_metric.width(self.receipt_length_label.text())
        self.receipt_length_label.setMaximumWidth(width)
        self.receipt_length_label_qty: QLabel = QLabel()
        self.receipt_length_label_qty.setText("")
        self.receipt_length_label_qty.setMaximumWidth(180)

        self.info_grid.addWidget(self.receipt_id_label, 0, 0)
        self.info_grid.addWidget(self.receipt_id_edit, 0, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.receipt_select, 0, 2)
        self.info_grid.addWidget(self.receipt_status_label, 1, 0)
        self.info_grid.addWidget(self.receipt_status_edit, 1, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.date_submitted_label, 2, 0)
        self.info_grid.addWidget(self.date_submitted_edit, 2, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.submitted_by_label, 3, 0)
        self.info_grid.addWidget(self.submitted_by_edit, 3, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.receipt_length_label, 4, 0)
        self.info_grid.addWidget(self.receipt_length_label_qty, 4, 1, alignment=Qt.AlignLeft)

    def lookup_process(self):
        d = ItemSelectDialog(self)
        d.setFont(self.font())
        result = d.exec_()
        if result:
            self.itemSelected.emit(d.selected_id)
            
    def setFields(self, id, status, date_submitted, submitted_by, length):
        self.receipt_id_edit.setText(id)
        self.receipt_status_edit.setText(status)
        self.date_submitted_edit.setText(date_submitted)
        self.submitted_by_edit.setText(submitted_by)
        self.receipt_length_label_qty.setText(length)

class ReceiptInfoWidget(QWidget):
    itemSelected = pyqtSignal(int)
    vendorSelected = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()

        self.main_horizontal_layout: QHBoxLayout = QHBoxLayout()

        self.info_group: ReceiptInfoGroup = ReceiptInfoGroup()
        self.info_group.itemSelected.connect(self.pass_item_selected)
        self.vendor_group: ReceiptVendorGroup = ReceiptVendorGroup()
        self.vendor_group.vendorSelected.connect(self.pass_vendor_selected)
        self.frame: QFrame = QFrame()

        self.main_horizontal_layout.addWidget(self.info_group)
        self.main_horizontal_layout.addWidget(self.vendor_group)
        self.main_horizontal_layout.addWidget(self.frame, stretch=1)

        self.setLayout(self.main_horizontal_layout)

    def pass_item_selected(self, this_id: int):
        self.itemSelected.emit(this_id)

    def pass_vendor_selected(self, this_id: int):
        self.vendorSelected.emit(this_id)

    def setFields(self, id, status, date_submitted, submitted_by, receipt_length, vendor_name, vendor_phone, vendor_address):
        self.info_group.setFields(
            id, status, date_submitted, submitted_by, receipt_length
        )
        self.vendor_group.setFields(
            vendor_name, vendor_phone, vendor_address
        )

class ReceiptsSubToolbar(QToolBar):
    addRow = pyqtSignal()
    editRow = pyqtSignal()
    deleteRow = pyqtSignal()
    resolveLines = pyqtSignal()

    def __init__(self, title):
        super().__init__(title)

        self.setIconSize(QSize(24, 24)) 
        self.setStyleSheet("""
            QToolBar {
                background: #f5f5f5;  /* Background color */
                border: 1px solid #f5f5f5;
                border-radius: 10px;
            }
            QToolBar::content {
                background: #333;
            }
            QToolBar::pane {
                background: rgba(0, 0, 0, 100);
                margin: 8px;
            }
            QToolButton {
                margin: 0px;
                padding: 0px;
            }
            QToolButton:hover {
                background: #f5f5f5;
            }
            """)

        self.resolve_action: QAction = QAction("&Resolve Line", self)
        self.resolve_action.triggered.connect(self.resolveLines.emit)

        self.add_action: QAction = QAction("&Add", self)
        self.add_action.triggered.connect(self.addRow.emit)

        self.edit_action: QAction = QAction("&Edit", self)
        self.edit_action.triggered.connect(self.editRow.emit)

        self.delete_row_action: QAction = QAction("&Delete", self)
        self.delete_row_action.triggered.connect(self.deleteRow.emit)

        self.addAction(self.resolve_action)
        self.addSeparator()
        self.addAction(self.add_action)
        self.addAction(self.edit_action)
        self.addAction(self.delete_row_action)

    def setStates(self, state):
        self.add_action.setDisabled(state)
        self.delete_row_action.setDisabled(state)

class ReceiptItemsTree(QTreeWidget):
    resolveLines = pyqtSignal(list)

    def __init__(self) -> None:
        super().__init__()
        self.inv_items = {}

        self.setHeaderLabels(["Type", "Barcode", "Product Name", "Qty", "Subtype", 
                              "Cost", "Packaging", "Expires", "Expiry Date", "Safety Stock", "Status"])
        self.setAlternatingRowColors(True)
        self.itemDoubleClicked.connect(print)

    def delete_item(self):
        barcode = self.selectedItems()[0].data["barcode"]
        if barcode:
            del self.inv_items[barcode]
            self.refresh_list()

    def resolve_line(self):
        items = sorted(set([item.data["id"] for item in self.selectedItems()]))
        if items:
            self.resolveLines.emit(items)

    def set_items(self, items: dict):
        self.inv_items = items
    
    def get_items(self) -> dict:
        return self.inv_items

    def edit_row(self):
        barcode = self.selectedItems()[0].data["barcode"]
        item = self.inv_items[barcode]
        d = ItemDialog(self)
        d.setFont(self.font())
        for key in ["sub_type", "cost", "product_quantity_unit", "expires", "safety_stock"]:
            if key not in item[5].keys():
                item[5][key] = "unknown"

        d.setFields(
            item_type=item[1],
            barcode=item[2],
            name=item[3],
            qty=item[4],
            subtype=item[5]["sub_type"],
            cost=item[5]["cost"],
            safety_stock=item[5]["safety_stock"],
            packaging=item[5]["product_quantity_unit"],
            expires=item[5]["expires"]
        )

        d.setEditMode(True)
        result = d.exec_()
        if result:
            row = d.getFields()
            barcode = row[2]
            self.inv_items[row[2]] = row
            self.refresh_list()

    def add_row(self):
        d = ItemDialog(self)
        d.setFont(self.font())
        result = d.exec_()
        if result:
            row = d.getFields()
            barcode = row[2]
            qty = row[4]
            item_id = row[0]
            if barcode in self.inv_items.keys():
                qty += self.inv_items[barcode][4]
                item_id = self.inv_items[barcode][0]
            row[4] = qty
            row[0] = item_id
            self.inv_items[row[2]] = row
            self.refresh_list()

    def refresh_list(self):
        self.clear()  
        for barcode, value in self.inv_items.items():
            listItem = ClickableTreeWidgetItem({"id": value[0], "barcode": barcode})

            listItem.setText(0, value[1])
            listItem.setText(1, barcode)
            listItem.setText(2, value[3])
            listItem.setText(3, str(value[4]))
    

            data: dict = value[5]
            sub_type = "OTHER"
            if "sub_type" in data.keys():
                sub_type = data['sub_type']
            listItem.setText(4, sub_type)

            my_keys = ["cost", "product_quantity_unit", "expires", "Expiry Date", "safety_stock"]
            
            y = 5
            for key in my_keys:
                if key in data.keys():
                    listItem.setText(y, str(data[key]))
                y += 1
            item_state = value[6]
            listItem.setText(10, item_state)
            if item_state != "Unresolved":
                listItem.setDisabled(True)
            self.addTopLevelItem(listItem)

class ReceiptSubwindow(QMdiSubWindow):
    closed = pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()
        self.status_bar: QStatusBar = QStatusBar()
        self.toolbar: ReceiptMainToolbar = ReceiptMainToolbar("Main Toolbar")
        self.main_widget: QWidget = QWidget()
        self.top_widget: ReceiptInfoWidget = ReceiptInfoWidget()
        self.top_widget.itemSelected.connect(self.load_receipt)
        self.top_widget.vendorSelected.connect(self.vendor_selected)

        self.table_toolbar: ReceiptsSubToolbar = ReceiptsSubToolbar("Sub Toolbar")
        self.item_tree: ReceiptItemsTree = ReceiptItemsTree()
        self.main_ver_layout: QVBoxLayout = QVBoxLayout()

        self.main_ver_layout.addWidget(self.toolbar)
        self.main_ver_layout.addWidget(self.top_widget)
        self.main_ver_layout.addWidget(self.table_toolbar)
        self.main_ver_layout.addWidget(self.item_tree, stretch=2)
        self.main_ver_layout.addWidget(self.status_bar)

        self.main_widget.setLayout(self.main_ver_layout)
        self.setWidget(self.main_widget)
        self.toolbar.installEventFilter(self)
        self.setWindowTitle("Receipts")

        self.vendor = None
        self.receipt = None

        self.toolbar.buttonHovered.connect(self.show_status_message)
        self.toolbar.saveReceipt.connect(self.save_receipt)
        self.toolbar.addReceipt.connect(self.add_receipt)

        self.table_toolbar.resolveLines.connect(self.item_tree.resolve_line)
        self.table_toolbar.addRow.connect(self.item_tree.add_row)
        self.table_toolbar.editRow.connect(self.item_tree.edit_row)
        self.table_toolbar.deleteRow.connect(self.item_tree.delete_item)
        self.item_tree.resolveLines.connect(self.resolve_line)

    def resolve_line(self, items):
        success, messages = database.resolve_receipt_line(self.receipt[0], items)
        msgbox = QMessageBox()
        str_line = "\n".join(messages)
        msgbox.setText(str_line)
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec_()
        if success:
            self.load_receipt(self.receipt[0])
    
    def add_receipt(self):
        now = datetime.datetime.now()
        payload = {
            "receipt": [f"PR-{helpers.random_tag(8)}", [], "Unresolved", str(now), "ERP", 0, []]
            }
        success, message, receipt_id = database.insert_receipt(payload)

        if success:
            self.load_receipt(receipt_id)
        else:
            msgbox = QMessageBox()
            msgbox.setText(message)
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.exec_()

    def save_receipt(self):
        database.update_receipt(self.receipt[0], {"receipt_items": self.item_tree.get_items(), "vendor_id": self.receipt[6]})
        self.load_receipt(self.receipt[0])

    def vendor_selected(self, this_id: int):
        self.receipt[6] = this_id
        self.save_receipt()
        self.vendor = database.fetch_vendor(self.receipt[6])
        self.setFields(self.receipt, self.vendor)

    def load_receipt(self, this_id):
        self.receipt = database.fetch_receipt(this_id)
        self.vendor = database.fetch_vendor(self.receipt[6])
        if not self.vendor:
            self.vendor = ["", "", "", "", "", ""]
        self.setFields(self.receipt, self.vendor)

    def setFields(self, receipt, vendor):
        self.top_widget.setFields(
            id=receipt[1],
            status=receipt[3],
            date_submitted=receipt[4],
            submitted_by=receipt[5],
            receipt_length=str(len(receipt[2])),
            vendor_name=vendor[1],
            vendor_phone=vendor[5],
            vendor_address=vendor[2]
        )
        self.item_tree.set_items(receipt[2])
        self.item_tree.refresh_list()

    def show_status_message(self, message):
        self.status_bar.showMessage(message)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Leave:
            self.status_bar.clearMessage()
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.closed.emit("receipt_window")
        super().closeEvent(event)
