from PyQt5.QtWidgets import (QFrame, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QApplication, QMainWindow, QMdiArea, 
                             QMenuBar, QStyle, QSizePolicy, QAction, QWidget, QMdiSubWindow, QLabel, QToolBar, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, 
                             QMessageBox, QLineEdit, QStatusBar, QPushButton, QTextEdit)
import database, json, helpers
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics
from subwindows import vendor_window
from subwindows import receipts_window

class ClickableLListItem(QListWidgetItem):
    def __init__(self, receipt_id):
        super().__init__()
        self.receipt_id = receipt_id


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
        
        self.first_box_v_layout: QVBoxLayout = QVBoxLayout()
        self.list_view_widget = QWidget()

        self.second_box_v_layout: QVBoxLayout = QVBoxLayout()
        self.info_widget = QWidget()
        
        # first_box_v_layout
        self.list_view_widget.setLayout(self.first_box_v_layout)
        self.list_view_widget.setMaximumWidth(200)
        
        self.receipt_list: QListWidget = QListWidget()
        self.receipt_list.setAlternatingRowColors(True)
        self.receipt_list.setMinimumHeight(300)
        self.receipt_list.itemClicked.connect(self.load_receipt)
        
        self.list_frame: QFrame = QFrame()
        self.list_frame.setFrameStyle(QFrame.StyledPanel)

        self.first_box_v_layout.addWidget(self.receipt_list, stretch=1)
        self.first_box_v_layout.addWidget(self.list_frame, stretch=1)
        # end first_box_v_layout

        # second_box_v_layout
        #   split into top_info_widget and QTableWidget
        self.top_info_widget: QWidget = QWidget()
        self.top_info_h_layout: QHBoxLayout = QHBoxLayout()

        #   settings for widgets and layouts
        self.info_widget.setLayout(self.second_box_v_layout)
        self.info_widget.setMinimumWidth(500)
        #self.top_info_widget.setMinimumHeight(200)
        self.top_info_widget.setLayout(self.top_info_h_layout)
        
            # This all fits into the top_info_h_layout
        self.info_group: QGroupBox = QGroupBox()
        self.info_group.setTitle("Receipt Information")
        self.top_info_h_layout.addWidget(self.info_group)

        self.info_grid: QGridLayout = QGridLayout()
        self.info_group.setLayout(self.info_grid)

        # receipt_id, receipt_status, date_submitted, submitted_by, receipt_length, receipt_img
        self.receipt_id_label: QLabel = QLabel()
        self.receipt_id_label.setText("Receipt ID: ")
        font_metric = QFontMetrics(self.receipt_id_label.font())
        width = font_metric.width(self.receipt_id_label.text())
        self.receipt_id_label.setMaximumWidth(width)
        self.receipt_id_edit: QLineEdit = QLineEdit()
        self.receipt_id_edit.setMaximumWidth(180)

        self.receipt_status_label: QLabel = QLabel()
        self.receipt_status_label.setText("Receipt Status: ")
        font_metric = QFontMetrics(self.receipt_status_label.font())
        width = font_metric.width(self.receipt_status_label.text())
        self.receipt_status_label.setMaximumWidth(width)
        self.receipt_status_edit: QLineEdit = QLineEdit()
        self.receipt_status_edit.setMaximumWidth(180)

        self.date_submitted_label: QLabel = QLabel()
        self.date_submitted_label.setText("Date Submitted: ")
        font_metric = QFontMetrics(self.date_submitted_label.font())
        width = font_metric.width(self.date_submitted_label.text())
        self.date_submitted_label.setMaximumWidth(width)
        self.date_submitted_edit: QLineEdit = QLineEdit()
        self.date_submitted_edit.setMaximumWidth(180)

        self.submitted_by_label: QLabel = QLabel()
        self.submitted_by_label.setText("Submitted By: ")
        font_metric = QFontMetrics(self.submitted_by_label.font())
        width = font_metric.width(self.submitted_by_label.text())
        self.submitted_by_label.setMaximumWidth(width)
        self.submitted_by_edit: QLineEdit = QLineEdit()
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


        self.vendor_grid: QGridLayout = QGridLayout()
        
        self.vendor_group: QGroupBox = QGroupBox()
        self.vendor_group.setLayout(self.vendor_grid)
        self.vendor_group.setTitle("Vendor Information")
        self.top_info_h_layout.addWidget(self.vendor_group)

        self.vendor_name_label: QLabel = QLabel()
        self.vendor_name_label.setText("Name: ")
        font_metric = QFontMetrics(self.vendor_name_label.font())
        width = font_metric.width(self.vendor_name_label.text())
        self.vendor_name_label.setMaximumWidth(width)
        self.vendor_name_edit: QLineEdit = QLineEdit()
        self.vendor_name_edit.setMaximumWidth(180)
        self.vendor_select_button: QPushButton = QPushButton()
        self.vendor_select_button.setText("s")
        self.vendor_select_button.setMaximumWidth(30)
        self.vendor_select_button.clicked.connect(self.select_vendor)

        self.vendor_phone_label: QLabel = QLabel()
        self.vendor_phone_label.setText("Phone: ")
        font_metric = QFontMetrics(self.vendor_phone_label.font())
        width = font_metric.width(self.vendor_phone_label.text())
        self.vendor_phone_label.setMaximumWidth(width)
        self.vendor_phone_edit: QLineEdit = QLineEdit()
        self.vendor_phone_edit.setMaximumWidth(180)

        self.vendor_address_label: QLabel = QLabel()
        self.vendor_address_label.setText("Address: ")
        font_metric = QFontMetrics(self.vendor_address_label.font())
        width = font_metric.width(self.vendor_address_label.text())
        self.vendor_address_label.setMaximumWidth(width)
        self.vendor_address_edit: QTextEdit = QTextEdit()
        self.vendor_address_edit.setMaximumWidth(180)
        self.vendor_address_edit.setMaximumHeight(75)


        self.vendor_grid.addWidget(self.vendor_name_label, 0, 0)
        self.vendor_grid.addWidget(self.vendor_name_edit, 0, 1)
        self.vendor_grid.addWidget(self.vendor_select_button, 0, 2)

        self.vendor_grid.addWidget(self.vendor_phone_label, 1, 0)
        self.vendor_grid.addWidget(self.vendor_phone_edit, 1, 1)

        self.vendor_grid.addWidget(self.vendor_address_label, 2, 0)
        self.vendor_grid.addWidget(self.vendor_address_edit, 2, 1)


            # end

            # bottom level
        self.bottom_info_widget: QWidget = QWidget()
        self.bottom_info_v_layout: QVBoxLayout = QVBoxLayout()
        self.bottom_info_widget.setLayout(self.bottom_info_v_layout)


        self.table_toolbar = QToolBar("Sub Toolbar")
        self.table_toolbar.setIconSize(QSize(24, 24)) 
        self.table_toolbar.setStyleSheet("""
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

        self.add_action: QAction = QAction("&Add", self.table_toolbar)
        self.add_action.triggered.connect(self.add_item)

        self.delete_row_action: QAction = QAction("&Delete", self.table_toolbar)
        self.delete_row_action.triggered.connect(self.delete_item)



        self.table_toolbar.addAction(self.add_action)
        self.table_toolbar.addAction(self.delete_row_action)


        self.bottom_info_v_layout.addWidget(self.table_toolbar)

        self.items_table: QTableWidget = QTableWidget()
        self.items_table.setColumnCount(9)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.cellChanged.connect(self.cell_changed)
        self.items_table.setHorizontalHeaderLabels(["type", "bracode", "name", "qty", "cost", "packaging", "expires", "Safety Stock", "data"])
        self.bottom_info_v_layout.addWidget(self.items_table)
            #end
        #end
        
        self.second_box_v_layout.addWidget(self.top_info_widget)
        self.second_box_v_layout.addWidget(self.bottom_info_widget)

        # Build Main Toolbar
        self.toolbar = QToolBar("My toolbar")
        self.toolbar.setIconSize(QSize(24, 24)) 
        self.toolbar.setStyleSheet("""
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
        
        pixmapi = QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.save_action = QAction(icon, "&Save", self.toolbar)
        self.save_action.triggered.connect(self.save_receipt)

        pixmapi = QStyle.SP_DialogResetButton
        icon = self.style().standardIcon(pixmapi)
        self.refresh_action = QAction(icon, "&Refresh", self.toolbar)
        self.refresh_action.triggered.connect(self.refresh_receipt)
        self.refresh_action.setToolTip("Refreshes the current selected data, any unsaved changes will be lost!")
        
        # delete
        pixmapi = QStyle.SP_DialogDiscardButton
        icon = self.style().standardIcon(pixmapi)
        self.delete_action = QAction(icon, "&Delete", self.toolbar)
        self.delete_action.setToolTip("Deletes the current selected data, any unsaved changes will be lost!")
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        #help
        pixmapi = QStyle.SP_TitleBarContextHelpButton
        icon = self.style().standardIcon(pixmapi)
        self.help_action = QAction(icon, "&Help", self.toolbar)
        self.help_action.setToolTip("Opens a help document..")

        # Resolve
        pixmapi = QStyle.SP_DialogApplyButton
        icon = self.style().standardIcon(pixmapi)
        self.resolve_action = QAction(icon, "&Resolve", self.toolbar)
        self.resolve_action.setStatusTip("Resolves the Selected Receipt and sets it to Resolved and transacts it into the system.")
        self.resolve_action.hovered.connect(lambda: self.show_status_message(self.resolve_action.statusTip()))

        # Deny
        pixmapi = QStyle.SP_DialogCancelButton
        icon = self.style().standardIcon(pixmapi)
        self.deny_action = QAction(icon, "&Deny", self.toolbar)
        self.deny_action.setToolTip("Denies the Receipt and sets it to resolve; this means nothing is transacted into the system.")

        self.toolbar.addAction(self.resolve_action)
        self.toolbar.addAction(self.deny_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.refresh_action)
        self.toolbar.addAction(self.delete_action)  
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.help_action)

        # over all Widget is constructed! seperates main toolbar from content   
        self.main_widget.setLayout(self.main_vertical_layout)
        
        self.main_vertical_layout.addWidget(self.toolbar)
        self.main_vertical_layout.addWidget(self.internal_widget, stretch=1)
        self.main_vertical_layout.addWidget(self.status_bar)

        # Constructs second layer layout, seperating the list half from the main body.
        
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

    def select_vendor(self):
        d = receipts_window.VendorSelectDialog(self, self.vendor_id)
        result = d.exec_()
        if result:
            self.vendor_id = d.selected_id
            database.update_receipt(self.select_receipt_id, {"vendor_id": int(self.vendor_id)})
            self.refresh_receipt()

    def show_status_message(self, message):
        self.status_bar.showMessage(message)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Leave:
            self.status_bar.clearMessage()
        return super().eventFilter(obj, event)
 
    def refresh_receipt(self):
        receipt_item = self.receipt_list.selectedItems()[0]
        if self.select_receipt_id == receipt_item.receipt_id:
            self.load_receipt(receipt_item)

    def save_receipt(self):
        if self.select_receipt_id:
            payload = {"receipt_items": self.items}
            success = database.update_receipt(self.select_receipt_id, payload)
            print(success)
    
    def add_item(self):
        tag = f"%{helpers.random_tag(6)}%"
        self.items_table.insertRow(self.items_table.rowCount() + 1)
        self.items[tag] = ["Insert", tag, "", 0, {"cost": 0.00, "product_quantity_unit": "None", "safety_stock": 0, "expires": "No"}]
        self.refresh_ui()

    def delete_item(self):
        row = self.items_table.currentRow()
        if row == -1:
            return
        
        msgbox = QMessageBox()
        msgbox.setText("You are about to delete this item, do you wish to proceed?")
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        accepted = msgbox.exec_()

        if accepted == QMessageBox.Cancel:
            return
        
        barcode = self.items_table.item(row, 1).text()
        del self.items[barcode]
        self.refresh_ui()

    def cell_changed(self, row, column):
        barcode = self.items_table.item(row, 1).text()
        item = self.items[barcode]
        data = item[4]
        # 0-data_type, 1-barcode, 2-name, 3-qty, 4-data
        if column == 3:
            item[column] = int(self.items_table.item(row, column).text())
        elif column == 4:
            data["cost"] = float(self.items_table.item(row, column).text())
        elif column == 5:
            data["product_quantity_unit"] = self.items_table.item(row, column).text()
        elif column == 6:
            data["expires"] = self.items_table.item(row, column).text()
        elif column == 7:
            data["safety_stock"] = int(self.items_table.item(row, column).text())
        else:
            item[column] = self.items_table.item(row, column).text()
        
        item[4] = data
        self.items[barcode] = item
        
    def load_receipt(self, receipt_item):
        self.select_receipt_id = receipt_item.receipt_id
        receipt = database.fetch_receipt(self.select_receipt_id)
        # 0 = id
        # 1 = unique_tag
        self.unique_id = receipt[1]
        # 2 = items
        self.items = receipt[2]
        # 3 = resolved?
        self.state = receipt[3]
        # 4 = Date_submitted
        self.date_submitted = receipt[4]
        # 5 = submitted_by
        self.submitted_by = receipt[5]
        # 6 = vendor id
        self.vendor_id = receipt[6]

        if self.vendor_id != 0:
            vendor = database.fetch_vendor(self.vendor_id)
            self.vendor_name = vendor[1]
            self.vendor_phone = vendor[5]
            self.vendor_address = vendor[2]
        else:
            self.vendor_name = None
            self.vendor_phone = None
            self.vendor_address = None

        self.refresh_ui()

    def refresh_ui(self):
        self.receipt_id_edit.setText(self.unique_id)
        self.receipt_status_edit.setText(self.state)
        self.date_submitted_edit.setText(self.date_submitted)
        self.submitted_by_edit.setText(self.submitted_by)
        self.receipt_length_label_qty.setText(str(len(self.items.keys())))

        self.vendor_name_edit.setText(self.vendor_name)
        self.vendor_phone_edit.setText(self.vendor_phone)
        self.vendor_address_edit.setText(self.vendor_address)

        self.items_table.clearContents()  
        self.index = 0
        self.items_table.setRowCount(0)
        self.items_table.blockSignals(True)
        for item, value in self.items.items():
            self.items_table.insertRow(self.index)

            data_type = QTableWidgetItem(value[0])
            data_type.setFlags(data_type.flags() & ~Qt.ItemIsEditable)
            barcode: QTableWidgetItem = QTableWidgetItem(item)
            name = QTableWidgetItem(value[2])
            qty = QTableWidgetItem(str(value[3]))
            data_item = QTableWidgetItem(str(json.dumps(value[4])))

            data: dict = value[4]
            my_keys = ["cost", "product_quantity_unit", "expires", "safety_stock"]
            
            y = 4
            for key in my_keys:
                if key in data.keys():
                    item = QTableWidgetItem(str(data[key]))
                    self.items_table.setItem(self.index, y, item)
                y += 1
            
            self.items_table.setItem(self.index, 0, data_type)
            self.items_table.setItem(self.index, 1, barcode)
            self.items_table.setItem(self.index, 2, name)
            self.items_table.setItem(self.index, 3, qty)
            self.items_table.setItem(self.index, 8, data_item)


            self.index += 1
        self.items_table.blockSignals(False)

    def load_data(self):
        receipts = database.fetch_receipts()
        for receipt_id, ident in receipts:
            item = ClickableLListItem(receipt_id=ident)
            item.setText(receipt_id)
            self.receipt_list.addItem(item)

    def closeEvent(self, event):
        self.closed.emit("receipt_window")
        super().closeEvent(event)

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
            self.receipt_window = ReceiptsWindow()
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