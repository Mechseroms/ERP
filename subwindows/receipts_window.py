from PyQt5.QtWidgets import (QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QMdiArea, 
                             QMenuBar, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, QLabel, QToolBar, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, 
                             QMessageBox, QLineEdit, QStatusBar, QPushButton, QTextEdit, QTreeWidgetItem, QDialog, QTreeWidget, QComboBox)
import database, json, helpers, datetime
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QBrush, QColor

# TODO: build a files dialog that you can add, download, and delete a file from a receipt
# TODO: Data valadation in items_table for making sure QTY is not 0 and if the item expires then a date is given, also making sure the
#       barcode starts and ends with a percent symbol. This data validation should be done as cells change AND at the attempt to resolve
#       the receipt.
# TODO: Search Bar for receipts_list by text and state (unresolved, resolved, denied)
# TODO: Error/INFO dialogs for key operations like Deletion, resolving, denying, vendor change, etc.
# TODO: HAve API list items default to food, have inserted items default to Other in their respective subtype dropdowns.

class TableDropDown(QComboBox):
    subtypeChanged = pyqtSignal(QComboBox)
    def __init__(self, associatedBarcode) -> None:
        super().__init__()
        self.identifier = associatedBarcode
        self.currentTextChanged.connect(self.emitSignal)

    def emitSignal(self, combobox):
        self.subtypeChanged.emit(self)

class ClickableTreeWidgetItem(QTreeWidgetItem):
    """Created with the sole purpose of adding a data variable.

    Could just be my lack of knowledge at the moment, but this is the best way i could
    think about saving a unique id into an item to be called on later during signal calls.
    """
    def __init__(self, data: any = None) -> None:
        super().__init__()
        self.data = data

class ReceiptItemsList(QTableWidget):
    tableEdited = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setColumnCount(11)
        self.setAlternatingRowColors(True)
        self.cellChanged.connect(self.cell_changed)
        self.setHorizontalHeaderLabels(["Type", "Barcode", "Name", "Qty", "Subtype", "Cost", "Packaging", "Expires", "Expiry Date", "Safety Stock", "Data"])
        
        self.type_options = ['FOOD', 'FOOD_PLU', 'MEDICINE', 'HYGENIC', 'CLEANERS']

        self.itemDoubleClicked.connect(self.save_previous_value)
        self.itemClicked.connect(self.save_previous_value)

        self.inv_items = {}
        self.previous_value = None

    def save_previous_value(self, item):
        """ A function that is called in order to save the last cells changed for future backtracking """
        self.previous_value = item.text()

    def subtype_changed(self, combobox: TableDropDown):
        print(combobox.identifier)
        item = self.inv_items[combobox.identifier]
        data: dict = item[4]
        data['sub_type'] = combobox.currentText()
        self.tableEdited.emit()

    def cell_changed(self, row, column):
        self.blockSignals(True)
        if column == 1:
            new_barcode = self.item(row, column).text()
            state = 0
            state, data = helpers.barcode_changed(new_barcode)
            if state == 0:
                # TODO: Need to actually handle if the barcode already exists in the items list to add quantities together...
                if 'barcode' in data.keys() and data['barcode'] in self.inv_items.keys():
                    qty = int(self.inv_items[data['barcode']][3]) + int(self.item(row, 3).text())
                else:
                    qty = int(self.item(row, 3).text())


                self.item(row, column).setText(data["barcode"])
                self.inv_items[data['barcode']] = [
                    "Pantry",
                    data["barcode"],
                    data["name"],
                    qty,
                    data
                    ]
                del self.inv_items[self.previous_value]
            elif state == -1:
                self.item(row, column).setText(self.previous_value)
            else:
                self.inv_items[new_barcode] = self.inv_items[self.previous_value]
                self.inv_items[new_barcode][1] = new_barcode
                del self.inv_items[self.previous_value]
            
            self.blockSignals(False)
            self.tableEdited.emit()
            return
        
        barcode = self.item(row, 1).text()
        item = self.items[barcode]
        data = item[4]
        # 0-data_type, 1-barcode, 2-name, 3-qty, 4-data
        if column == 3:
            item[column] = int(self.item(row, column).text())
        elif column == 4:
            data["cost"] = str(self.item(row, column).text())
        elif column == 5:
            data["product_quantity_unit"] = self.item(row, column).text()
        elif column == 6:
            data["expires"] = self.item(row, column).text()
        elif column == 8:
            data["safety_stock"] = int(self.item(row, column).text())
        elif column == 7:
            data["Expiry Date"] = self.item(row, column).text()
        else:
            item[column] = self.item(row, column).text()
        
        item[4] = data
        self.inv_items[barcode] = item
        self.blockSignals(False)
        self.tableEdited.emit()
    
    def set_items(self, items: dict):
        self.inv_items = items
    
    def get_items(self):
        return self.inv_items
    
    def add_item(self):
        tag = f"%{helpers.random_tag(6)}%"
        self.insertRow(self.rowCount() + 1)
        self.inv_items[tag] = ["Insert", tag, "", 0, {"cost": 0.00, "product_quantity_unit": "None", "safety_stock": 0, "expires": "No"}]

    def delete_item(self):
        row = self.currentRow()
        if row == -1:
            return
        
        msgbox = QMessageBox()
        msgbox.setText("You are about to delete this item, do you wish to proceed?")
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        accepted = msgbox.exec_()

        if accepted == QMessageBox.Cancel:
            return
        
        barcode = self.item(row, 1).text()
        del self.inv_items[barcode]
        del self.items_combos[barcode]

    def refresh_table(self, state: str = "Unknown"):
        self.clearContents()  
        self.index = 0
        self.setRowCount(0)
        self.blockSignals(True)
        for item, value in self.inv_items.items():
            self.insertRow(self.index)
            data_type = QTableWidgetItem(value[0])
            barcode: QTableWidgetItem = QTableWidgetItem(item)
            name = QTableWidgetItem(value[2])
            if value[2] in ["", None]:
                name.setBackground(QBrush(QColor(255,102,102)))
            qty = QTableWidgetItem(str(value[3]))
            self.item_combobox: TableDropDown = TableDropDown(associatedBarcode=item)
            self.item_combobox.addItems(self.type_options)

            data_item = QTableWidgetItem(str(json.dumps(value[4])))
            
            if state != "Unresolved":
                data_type.setFlags(data_type.flags() & ~Qt.ItemIsEnabled)
                barcode.setFlags(barcode.flags() & ~Qt.ItemIsEnabled)
                name.setFlags(name.flags() & ~Qt.ItemIsEnabled)
                qty.setFlags(qty.flags() & ~Qt.ItemIsEnabled)
                data_item.setFlags(data_item.flags() & ~Qt.ItemIsEnabled)

            data: dict = value[4]

            if "sub_type" in data.keys():
                self.item_combobox.setCurrentText(data['sub_type'])

            self.item_combobox.subtypeChanged.connect(self.subtype_changed)

            my_keys = ["cost", "product_quantity_unit", "expires", "Expiry Date", "safety_stock"]
            
            y = 5
            for key in my_keys:
                if key in data.keys():
                    item = QTableWidgetItem(str(data[key]))
                    if state != "Unresolved":
                        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                    if key == "Expiry Date" and "expires" in data.keys() and data["expires"] == "yes":
                        item .setFlags(item.flags() & Qt.ItemIsEnabled)
                    self.setItem(self.index, y, item)
                y += 1
            
            self.setItem(self.index, 0, data_type)
            self.setItem(self.index, 1, barcode)
            self.setItem(self.index, 2, name)
            self.setItem(self.index, 3, qty)
            self.setCellWidget(self.index, 4, self.item_combobox)
            self.setItem(self.index, 10, data_item)


            self.index += 1
        self.blockSignals(False)

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

class ClickableLListItem(QListWidgetItem):
    def __init__(self, receipt_id):
        super().__init__()
        self.receipt_id = receipt_id

class ReceiptsMainToolbar(QToolBar):
    buttonHovered = pyqtSignal(str)
    denied = pyqtSignal()
    resolve = pyqtSignal()
    deleteReceipt = pyqtSignal()
    openFiles = pyqtSignal()
    addReceipt = pyqtSignal()
    openHelp = pyqtSignal()

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
        

        self.delete_action = QAction("&Delete", self)
        self.delete_action.setStatusTip("Deletes the current selected receipt, any unsaved changes will be lost!")
        self.delete_action.hovered.connect(lambda: self.buttonHovered.emit(self.delete_action.statusTip()))
        self.delete_action.triggered.connect(self.deleteReceipt.emit)

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
        self.addAction(self.delete_action)
        self.addSeparator()
        self.addAction(self.files_action)
        self.addWidget(spacer)
        self.addAction(self.help_action)

    def setStates(self, state):
        self.delete_action.setDisabled(state)
        self.resolve_action.setDisabled(state)
        self.deny_action.setDisabled(state)

class ReceiptsSubToolbar(QToolBar):
    addRow = pyqtSignal()
    deleteRow = pyqtSignal()

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

        self.add_action: QAction = QAction("&Add", self)
        self.add_action.triggered.connect(self.addRow.emit)

        self.delete_row_action: QAction = QAction("&Delete", self)
        self.delete_row_action.triggered.connect(self.deleteRow.emit)

        self.addAction(self.add_action)
        self.addAction(self.delete_row_action)

    def setStates(self, state):
        self.add_action.setDisabled(state)
        self.delete_row_action.setDisabled(state)

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
        self.info_grid.addWidget(self.receipt_status_label, 1, 0)
        self.info_grid.addWidget(self.receipt_status_edit, 1, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.date_submitted_label, 2, 0)
        self.info_grid.addWidget(self.date_submitted_edit, 2, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.submitted_by_label, 3, 0)
        self.info_grid.addWidget(self.submitted_by_edit, 3, 1, alignment=Qt.AlignLeft)
        self.info_grid.addWidget(self.receipt_length_label, 4, 0)
        self.info_grid.addWidget(self.receipt_length_label_qty, 4, 1, alignment=Qt.AlignLeft)

    def setFields(self, id, status, date_submitted, submitted_by, length):
        self.receipt_id_edit.setText(id)
        self.receipt_status_edit.setText(status)
        self.date_submitted_edit.setText(date_submitted)
        self.submitted_by_edit.setText(submitted_by)
        self.receipt_length_label_qty.setText(length)

class ReceiptListWidget(QWidget):
    itemClicked = pyqtSignal(QListWidgetItem)

    def __init__(self) -> None:
        super().__init__()

        self.first_box_v_layout: QVBoxLayout = QVBoxLayout()

        self.setLayout(self.first_box_v_layout)
        self.setMaximumWidth(200)
        
        self.receipt_list: QListWidget = QListWidget()
        self.receipt_list.setAlternatingRowColors(True)
        self.receipt_list.setMinimumHeight(300)
        self.receipt_list.itemClicked.connect(self.itemClicked.emit)
        
        self.list_frame: QFrame = QFrame()
        self.list_frame.setFrameStyle(QFrame.StyledPanel)

        self.first_box_v_layout.addWidget(self.receipt_list, stretch=1)
        self.first_box_v_layout.addWidget(self.list_frame, stretch=1)

    def clear_list(self):
        self.receipt_list.clear()

    def add_item(self, item):
        self.receipt_list.addItem(item)

    def add_items(self, receipts: list):
        self.receipt_list.clear()
        for receipt in receipts:
            row_id = receipt[0]
            unique_id = receipt[1]
            item = ClickableLListItem(receipt_id=row_id)
            statuses = {"Denied": "(D)", "Resolved": "(R)", "Unresolved": "(U)"}
            item.setText(f"{statuses[receipt[3]]} {unique_id}")
            self.receipt_list.addItem(item)

    def getSelectedItem(self):
        return self.receipt_list.selectedItems()[0]
    
class ReceiptsWindow(QMdiSubWindow):
    closed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.status_bar: QStatusBar = QStatusBar()

        self.main_widget = QWidget()
        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.internal_widget: QWidget = QWidget()
        self.main_horizontal_layout: QHBoxLayout = QHBoxLayout()
        
        self.list_view_widget = ReceiptListWidget()
        self.list_view_widget.itemClicked.connect(self.load_receipt)

        self.second_box_v_layout: QVBoxLayout = QVBoxLayout()
        self.info_widget = QWidget()

        self.top_info_widget: QWidget = QWidget()
        self.top_info_h_layout: QHBoxLayout = QHBoxLayout()

        self.info_widget.setLayout(self.second_box_v_layout)
        self.info_widget.setMinimumWidth(500)
        self.top_info_widget.setLayout(self.top_info_h_layout)
        self.top_info_widget.setMaximumWidth(500)
        
        self.info_group: ReceiptInfoGroup = ReceiptInfoGroup()
        self.info_group.setTitle("Receipt Information")
        self.top_info_h_layout.addWidget(self.info_group)

        self.vendor_group: ReceiptVendorGroup = ReceiptVendorGroup()
        self.vendor_group.setTitle("Vendor Information")
        
        self.top_info_h_layout.addWidget(self.vendor_group)

        self.bottom_info_widget: QWidget = QWidget()
        self.bottom_info_v_layout: QVBoxLayout = QVBoxLayout()
        self.bottom_info_widget.setLayout(self.bottom_info_v_layout)

        self.table_toolbar = ReceiptsSubToolbar("Sub Toolbar")
        
        self.bottom_info_v_layout.addWidget(self.table_toolbar)

        self.items_table: ReceiptItemsList = ReceiptItemsList()
        self.bottom_info_v_layout.addWidget(self.items_table)
        
        self.second_box_v_layout.addWidget(self.top_info_widget)
        self.second_box_v_layout.addWidget(self.bottom_info_widget)

        self.toolbar = ReceiptsMainToolbar("My toolbar")

        self.main_widget.setLayout(self.main_vertical_layout)
        
        self.main_vertical_layout.addWidget(self.toolbar)
        self.main_vertical_layout.addWidget(self.internal_widget, stretch=1)
        self.main_vertical_layout.addWidget(self.status_bar)
        
        self.main_horizontal_layout.addWidget(self.list_view_widget)
        self.main_horizontal_layout.addWidget(self.info_widget)
        self.internal_widget.setLayout(self.main_horizontal_layout)

        self.toolbar.installEventFilter(self)
        self.setWidget(self.main_widget)

        self.setWindowTitle("Receipts")
        self.load_data()

        self.select_receipt_id = None
        self.unique_id = None
        self.items = None
        self.state = None
        self.date_submitted = None
        self.submitted_by = None
        self.vendor_id = None
        self.vendor_name = None
        self.vendor_phone = None
        self.vendor_address = None

        self.vendor_group.vendorSelected.connect(self.select_vendor)
        self.toolbar.resolve.connect(self.resolve_receipt)
        self.toolbar.denied.connect(self.deny_receipt)
        self.toolbar.addReceipt.connect(self.add_receipt)
        self.toolbar.deleteReceipt.connect(self.delete_receipt)
        self.toolbar.buttonHovered.connect(self.show_status_message)
        self.table_toolbar.addRow.connect(self.add_item)
        self.table_toolbar.deleteRow.connect(self.delete_item)
        self.items_table.tableEdited.connect(self.process_table_change)

    def process_table_change(self):
        self.save_receipt()
        self.refresh_receipt()

    def add_receipt(self):
        now = datetime.datetime.now()
        payload = {
            "receipt_id": f"PR-{helpers.random_tag(8)}",
            "receipt_items": {},
            "receipt_status": "Unresolved",
            "date_submitted": str(now),
            "submitted_by": "test_pos",
            "vendor_id": 0,
            "files": []
        }
        success = database.insert_receipt(payload)

        if success:
            self.load_data()

    def delete_receipt(self):
        print(f"Deleting {self.select_receipt_id}..")

    def select_vendor(self, vendor_id: int):
        self.vendor_id = vendor_id
        self.save_receipt()
        self.refresh_receipt()

    def show_status_message(self, message):
        self.status_bar.showMessage(message)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Leave:
            self.status_bar.clearMessage()
        return super().eventFilter(obj, event)

    def save_receipt(self):
        if self.select_receipt_id:
            payload = {"receipt_items": self.items_table.get_items(), "vendor_id": int(self.vendor_id)}
            database.update_receipt(self.select_receipt_id, payload)

    def refresh_receipt(self):
        selected_item = self.list_view_widget.getSelectedItem()
        if self.select_receipt_id == selected_item.receipt_id:
            self.load_receipt(selected_item)

    def deny_receipt(self):
        if self.select_receipt_id:
            self.save_receipt()
            success = database.deny_receipt(self.select_receipt_id)
            if success:
                self.refresh_receipt()
                self.load_data()

    def resolve_receipt(self):
        if self.select_receipt_id:
            self.save_receipt()
            success = database.resolve_receipt(self.select_receipt_id)
            if success:
                self.refresh_receipt()
                self.load_data()     

    def load_receipt(self, receipt_item):
        self.select_receipt_id = receipt_item.receipt_id
        receipt = database.fetch_receipt(self.select_receipt_id)
        # 0 = id
        # 1 = unique_tag
        self.unique_id = receipt[1]
        # 2 = items
        self.items = receipt[2]
        self.items_table.set_items(self.items)
        # 3 = resolved?
        self.state = receipt[3]
        # 4 = Date_submitted
        self.date_submitted = receipt[4]
        # 5 = submitted_by
        self.submitted_by = receipt[5]
        # 6 = vendor id
        self.vendor_id = receipt[6]
        self.vendor_group.setVendorId(self.vendor_id)

        if self.vendor_id != 0:
            vendor = database.fetch_vendor(self.vendor_id)
            self.vendor_name = vendor[1]
            self.vendor_phone = vendor[5]
            self.vendor_address = vendor[2]
        else:
            self.vendor_name = None
            self.vendor_phone = None
            self.vendor_address = None

        if self.state != "Unresolved":
            self.toolbar.setStates(True)
            self.table_toolbar.setStates(True)
            self.vendor_group.setStates(True)
            
        else:
            self.toolbar.setStates(False)
            self.table_toolbar.setStates(False)
            self.vendor_group.setStates(False)

        self.refresh_ui()

    def refresh_ui(self):
        self.info_group.setFields(
            self.unique_id,
            self.state,
            self.date_submitted,
            self.submitted_by,
            str(len(self.items.keys()))
        )

        self.vendor_group.setFields(
            self.vendor_name,
            self.vendor_phone,
            self.vendor_address
        )

        self.items_table.refresh_table(state=self.state)

    def load_data(self):
        receipts = database.fetch_receipts()
        self.list_view_widget.add_items(receipts)

    def closeEvent(self, event):
        self.refresh_receipt()
        self.closed.emit("receipt_window")
        super().closeEvent(event)

    def add_item(self):
        self.items_table.add_item()
        self.save_receipt()
        self.refresh_receipt()

    def delete_item(self):
        self.items_table.delete_item()
        self.save_receipt()
        self.refresh_receipt()
