from PyQt5.QtWidgets import (QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QMdiArea, 
                             QMenuBar, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, QLabel, QToolBar, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, 
                             QMessageBox, QLineEdit, QTextEdit)
import database, json, helpers, datetime
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont

class ClickableLListItem(QListWidgetItem):
    def __init__(self, vendor_id):
        super().__init__()
        self.vendor_id = vendor_id

class VendorToolBar(QToolBar):
    new = pyqtSignal()
    save = pyqtSignal()
    delete = pyqtSignal()

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
        
        self.new_action: QAction = QAction("&New", self)
        self.new_action.triggered.connect(self.new.emit)
        self.save_action: QAction = QAction("&Save", self)
        self.save_action.triggered.connect(self.save.emit)
        self.delete_action: QAction = QAction("&Delete", self)
        self.delete_action.triggered.connect(self.delete.emit)
        self.help_action: QAction = QAction("&Help", self)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.addActions([self.new_action, self.save_action, self.delete_action])
        self.addWidget(spacer)
        self.addAction(self.help_action)

class VendorList(QWidget):
    selectionChanged = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        
        self.vertical_layout: QVBoxLayout = QVBoxLayout()
        self.vendor_list: QListWidget = QListWidget()
        self.vendor_list.itemClicked.connect(self.selection_changed)

        self.vertical_layout.addWidget(self.vendor_list, stretch=1)

        self.setLayout(self.vertical_layout)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.selected_index = None

    def selection_changed(self, item):
        self.selected_index = item.vendor_id
        self.selectionChanged.emit(item.vendor_id)

    def refresh_ui(self, vendors: list):
        self.vendor_list.clear()
        index = 1
        for vendor in vendors:
            item = ClickableLListItem(vendor_id=vendor[0])
            item.setText(f"{index}. {vendor[1]}")
            self.vendor_list.addItem(item)
            index += 1

class VendorForm(QWidget):
    formChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.vertical_layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.grid_layout: QGridLayout = QGridLayout()
        self.info_group: QGroupBox = QGroupBox()
        self.info_group.setLayout(self.grid_layout)
        self.info_group.setTitle("Vendor Information")
        self.vertical_layout.addWidget(self.info_group)
        # name
        self.vendor_name_label: QLabel = QLabel()
        self.vendor_name_label.setText("Vendor Name: ")
        self.vendor_name_edit: QLineEdit = QLineEdit()
        self.vendor_name_edit.setText("")
        self.vendor_name_edit.setMaximumWidth(180)
        self.vendor_name_edit.textChanged.connect(self.formChanged.emit)

        self.phone_number_label: QLabel = QLabel()
        self.phone_number_label.setText("Phone Number: ")
        self.phone_number_edit: QLineEdit = QLineEdit()
        self.phone_number_edit.setText("")
        self.phone_number_edit.setMaximumWidth(180)
        self.phone_number_edit.textChanged.connect(self.formChanged.emit)
        #address
        self.vendor_address_label: QLabel = QLabel()
        self.vendor_address_label.setText("Vendor Address: ")
        self.vendor_address_edit: QTextEdit = QTextEdit()
        self.vendor_address_edit.setText("")
        self.vendor_address_edit.setMaximumWidth(180)
        self.vendor_address_edit.setMaximumHeight(100)
        self.vendor_address_edit.textChanged.connect(self.formChanged.emit)

        #created_by
        self.created_by_label: QLabel = QLabel()
        self.created_by_label.setText("Created By: ")
        self.created_by_edit: QLineEdit = QLineEdit()
        self.created_by_edit.setText("")
        self.created_by_edit.setMaximumWidth(180)
        self.created_by_edit.textChanged.connect(self.formChanged.emit)

        #creation_date
        self.creation_date_label: QLabel = QLabel()
        self.creation_date_label.setText("Creation Date: ")
        self.creation_date_edit: QLineEdit = QLineEdit()
        self.creation_date_edit.setText("")
        self.creation_date_edit.setMaximumWidth(180)
        self.creation_date_edit.textChanged.connect(self.formChanged.emit)

        self.grid_layout.addWidget(self.vendor_name_label, 0, 0)
        self.grid_layout.addWidget(self.vendor_name_edit, 0, 1)

        self.grid_layout.addWidget(self.phone_number_label, 1, 0)
        self.grid_layout.addWidget(self.phone_number_edit, 1, 1)

        self.grid_layout.addWidget(self.vendor_address_label, 2, 0)
        self.grid_layout.addWidget(self.vendor_address_edit, 2, 1)

        self.grid_layout.addWidget(self.created_by_label, 3, 0)
        self.grid_layout.addWidget(self.created_by_edit, 3, 1)

        self.grid_layout.addWidget(self.creation_date_label, 4, 0)
        self.grid_layout.addWidget(self.creation_date_edit, 4, 1)

    def refresh_ui(self, data: dict):
        self.vendor_name_edit.setText(data['name'])
        self.vendor_address_edit.setText(data['address'])
        self.creation_date_edit.setText(data['creation_date'])
        self.created_by_edit.setText(data['created_by'])
        self.phone_number_edit.setText(data['phone_number'])

    def clear_form(self):
        self.vendor_name_edit.setText("")
        self.vendor_address_edit.setText("")
        self.creation_date_edit.setText("")
        self.created_by_edit.setText("")
        self.phone_number_edit.setText("")

class VendorWindow(QMdiSubWindow):
    closed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self.internal_widget: QWidget = QWidget()
        self.setWidget(self.internal_widget)

        self.main_ver_layout: QVBoxLayout = QVBoxLayout()
        self.main_ver_layout.setContentsMargins(0, 0, 0, 0)

        #nests inside main_ver_layout
        self.main_hor_layout: QHBoxLayout = QHBoxLayout()

        #list of vendors
        self.vendor_list = VendorList()
        self.vendor_list.selectionChanged.connect(self.load_vendor)
        self.vendor_form = VendorForm()
        self.vendor_form.formChanged.connect(self.fields_changed)
        
        self.toolbar = VendorToolBar("Vendor Toolbar")
        self.toolbar.new.connect(self.add_vendor)
        self.toolbar.save.connect(self.save_vendor)
        self.toolbar.delete.connect(self.delete_vendor)

        
        
        self.main_ver_layout.addWidget(self.toolbar)
        self.main_ver_layout.addLayout(self.main_hor_layout)

        self.main_hor_layout.addWidget(self.vendor_list)
        self.main_hor_layout.addWidget(self.vendor_form)

        self.internal_widget.setLayout(self.main_ver_layout)
        self.setWindowTitle("Vendors")
        self.load_data()

        self.selected_vendor_id = None
        self.vendor_name = None
        self.vendor_address = None
        self.creation_date = None
        self.created_by = None
        self.phone_number = None

    def save_vendor(self):
        if not self.selected_vendor_id:
            return
        payload = {
            'name': self.vendor_name,
            'address': self.vendor_address,
            'creation_date': str(self.creation_date),
            'created_by': self.created_by,
            'phone_number': self.phone_number
        }
        success = database.update_vendor(self.selected_vendor_id, payload)
        if success:
            self.load_data()

    def delete_vendor(self):
        if not self.selected_vendor_id:
            return
        
        msgbox = QMessageBox()
        msgbox.setText(f"You are about to Delete {self.vendor_name} from the database, do you wish to proceed?")
        msgbox.setInformativeText("Once this opertion completes, the vendor will be gone forever!")
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        accepted = msgbox.exec_()
    
        if accepted == QMessageBox.Cancel:
            return
        
        database.delete_vendor(self.selected_vendor_id)
        self.load_data()
        self.vendor_form.clear_form()
        self.vendor_name = None
        self.setWindowTitle(f"Vendors")
        self.vendor_address = None
        self.creation_date = None
        self.created_by = None
        self.phone_number = None

    def fields_changed(self):
        self.vendor_name = self.vendor_form.vendor_name_edit.text()
        self.setWindowTitle(f"Vendors - {self.vendor_name}({self.selected_vendor_id})")
        self.vendor_address = self.vendor_form.vendor_address_edit.toPlainText()
        self.creation_date = self.vendor_form.creation_date_edit.text()
        self.created_by = self.vendor_form.created_by_edit.text()
        self.phone_number = self.vendor_form.phone_number_edit.text()

    def load_vendor(self, vendor_id):
        vendor = database.fetch_vendor(vendor_id)
        self.selected_vendor_id = vendor[0]
        self.vendor_name = vendor[1]
        self.vendor_address = vendor[2]
        self.creation_date = vendor[3]
        self.created_by = vendor[4]
        self.phone_number = vendor[5]
        
        self.vendor_form.refresh_ui({
            'name': self.vendor_name,
            'address': self.vendor_address,
            'creation_date': self.creation_date,
            'created_by': self.created_by,
            'phone_number': self.phone_number
        })

    def add_vendor(self):
        date = datetime.datetime.now()
        default_vendor = ["New Vendor", "", str(date), "", ""]
        success = database.insert_vendor(default_vendor)
        if not success:
            print("raise error please")
        self.load_data()
        self.vendor_form.clear_form()
        self.vendor_name = None
        self.setWindowTitle(f"Vendors")
        self.vendor_address = None
        self.creation_date = None
        self.created_by = None
        self.phone_number = None

    def load_data(self):
        vendors = database.fetch_vendors()
        self.vendor_list.refresh_ui(vendors)

    def closeEvent(self, event):
        self.closed.emit("vendor_window")
        super().closeEvent(event)