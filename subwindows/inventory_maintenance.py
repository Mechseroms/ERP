from PyQt5.QtWidgets import (QMdiSubWindow, QStatusBar, QWidget, QVBoxLayout, QToolBar, QHBoxLayout, QAction, QGridLayout, QLineEdit,
                             QPushButton, QListWidget, QListWidgetItem, QLabel, QGroupBox, QFrame, QStyle, QDialog, QTreeWidgetItem, 
                             QTreeWidget, QComboBox, QCheckBox, QTabBar, QTabWidget)
from PyQt5.QtCore import pyqtSignal, QSize, QEvent, Qt
from PyQt5.QtGui import QFontMetrics, QFont
import database

class ClickableTreeWidgetItem(QTreeWidgetItem):
    """Created with the sole purpose of adding a data variable.

    Could just be my lack of knowledge at the moment, but this is the best way i could
    think about saving a unique id into an item to be called on later during signal calls.
    """
    def __init__(self, data: any = None) -> None:
        super().__init__()
        self.data = data

class ClickableLListItem(QListWidgetItem):
    def __init__(self, item_id):
        super().__init__()
        self.item_id = item_id

class InventoryMainToolbar(QToolBar):
    buttonHovered = pyqtSignal(str)

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

        """
        add inventory item
        delete inventory item
        attach files
        seperator
        archive item
        transactions
        locations
        spacer
        help
        """ 

        self.add_item_action = QAction("&Add", self)
        self.add_item_action.setStatusTip("Adds a new item to the database.")
        self.add_item_action.hovered.connect(lambda: self.buttonHovered.emit(self.add_item_action.statusTip()))

        self.addAction(self.add_item_action)

class ItemSelectDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.grid_layout: QGridLayout = QGridLayout()

        self.search_input: QLineEdit = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setStyleSheet("border-radius: 20px;")
        self.search_input.setFixedHeight(30)

        self.item_tree: QTreeWidget = QTreeWidget(self)
        self.item_tree.setHeaderLabels(["ID", "Barcode", "Item Name", "Brand"])
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

        self.back_arrow: QPushButton = QPushButton()
        self.back_arrow.setText("<-")
        self.back_arrow.setStyleSheet(st)
        self.back_arrow.clicked.connect(self.last_page)

        self.current_page = 1
        self.total_pages = 0
        self.last_search = ""
        self.page_label: QLabel = QLabel()
        self.page_label.setText(f"{self.current_page}/{self.total_pages}")

        self.foreward_arrow: QPushButton = QPushButton()
        self.foreward_arrow.setText("->")
        self.foreward_arrow.setStyleSheet(st)
        self.foreward_arrow.clicked.connect(self.next_page)

        self.grid_layout.addWidget(self.search_input, 0, 0, 1, 3)
        self.grid_layout.addWidget(self.item_tree, 1, 0, 1, 7)

        self.grid_layout.addWidget(self.back_arrow, 2, 2)
        self.grid_layout.addWidget(self.page_label, 2, 3, 1, 1, Qt.AlignCenter)
        self.grid_layout.addWidget(self.foreward_arrow, 2, 4)

        self.setLayout(self.grid_layout)
        self.setWindowTitle("Select Inventory Item...")
        self.resize(1000, 300)

        self.selected_id = 0
        self.load_data()

    def next_page(self):
        self.current_page += 1
        self.load_data()
    
    def last_page(self):
        self.current_page -= 1
        self.load_data()

    def load_data(self):
        search_query = self.search_input.text()
        if search_query != self.last_search:
            self.total_pages = 0
            self.current_page = 1
            self.last_search = self.search_input.text()
        
        success, data = database.fetch_pantry_paginated(self.current_page, search_query)

        if success:
            self.total_pages = data['total_pages']
            self.page_label.setText(f"{self.current_page} / {self.total_pages}")
            items = data['items']

            self.item_tree.clear()
            for item in items:
                listItem = ClickableTreeWidgetItem(item[0])
                listItem.setText(0, str(item[0]))
                listItem.setText(1, str(item[1]))
                listItem.setText(2, str(item[2]))
                listItem.setText(3, str(item[3]))
                self.item_tree.addTopLevelItem(listItem)

        self.item_tree.setTextElideMode(Qt.ElideRight)
        self.item_tree.setColumnWidth(0, 50)
        self.item_tree.setColumnWidth(1, 100)
        self.item_tree.setColumnWidth(2, 400)
        self.item_tree.setColumnWidth(3, 100)
    
    def closeEvent(self, event):
        self.reject()
        super().closeEvent(event)

    def new_selected(self, value):
        self.selected_id = value.data
        self.accept()

class BasicInfoWidget(QWidget):
    itemSelected = pyqtSignal(int)

    def __init__(self, font=None) -> None:
        super().__init__()
        
        if font is None:
            font = self.font()
        else:
            self.setFont(font)

        self.main_horizontal_layout: QHBoxLayout = QHBoxLayout()

        # group
        self.lookup_group: LookupGroup = LookupGroup(font)
        self.lookup_group.itemSelected.connect(self.lookup_process)
        
        self.config_group = ItemConfigWidget(font)

        self.filler_frame: QFrame = QFrame()
        self.filler_frame.setStyleSheet("background-color: blue;")

        self.main_horizontal_layout.addWidget(self.lookup_group)
        self.main_horizontal_layout.addWidget(self.config_group)
        self.main_horizontal_layout.addWidget(self.filler_frame, 2)
        self.setLayout(self.main_horizontal_layout)
        self.main_horizontal_layout.setContentsMargins(0, 0, 0, 0)

    def lookup_process(self, _id):
        self.itemSelected.emit(_id)

    def setFields(self, _id, _name, _barcode, _entry_type, _subtype, _ai_pickable, _expires):
        self.lookup_group.setFields(_id, _barcode, _name)
        self.config_group.setFields(
            _entry_type,
            _subtype,
            _ai_pickable,
            _expires
        )

class LookupGroup(QGroupBox):
    itemSelected = pyqtSignal(int)

    def __init__(self, font=None):
        super().__init__()

        if font is None:
            font = self.font()
        else:
            self.setFont(font)

        self.grid_layout: QGridLayout = QGridLayout()
        
        self.setTitle("Basic Info")
        self.setLayout(self.grid_layout)

        self.id_field: QLineEdit = QLineEdit()
        self.id_field.setFont(font)

        self.id_label: QLabel = QLabel()
        self.id_label.setFont(font)
        self.id_label.setText("ID:")
        font_metric = QFontMetrics(self.id_label.font())
        width = font_metric.width(self.id_label.text())
        self.id_label.setMaximumWidth(width)
        self.id_field.setReadOnly(True)
        self.id_field.setMinimumWidth(160)

        self.lookup_field: QLineEdit = QLineEdit()
        self.lookup_field.setFont(font)
        self.lookup_field.setMinimumWidth(160)

        self.lookup_label: QLabel = QLabel()
        self.lookup_label.setFont(font)
        self.lookup_label.setText("Barcode: ")
        font_metric = QFontMetrics(self.lookup_label.font())
        width = font_metric.width(self.lookup_label.text())
        self.lookup_label.setMaximumWidth(width)
        self.lookup_field.setReadOnly(True)

        self.lookup_search: QPushButton = QPushButton()
        self.lookup_search.setFont(font)
        self.lookup_search.setText("lookup")
        self.lookup_search.clicked.connect(self.lookup_process)
        self.lookup_search.setMaximumSize(60, 25)

        self.name_field: QLineEdit = QLineEdit()
        self.name_field.setFont(font)
        self.name_field.setMinimumWidth(160)

        self.name_label: QLabel = QLabel()
        self.name_label.setFont(font)
        self.name_label.setText("Name: ")
        font_metric = QFontMetrics(self.name_label.font())
        width = font_metric.width(self.name_label.text())
        self.name_label.setMaximumWidth(width)
        self.name_field.setReadOnly(True)

        self.grid_layout.addWidget(self.id_label, 0, 0)
        self.grid_layout.addWidget(self.id_field, 0, 1)

        self.grid_layout.addWidget(self.lookup_label, 1, 0)
        self.grid_layout.addWidget(self.lookup_field, 1, 1, 1, 2)
        self.grid_layout.addWidget(self.lookup_search, 1, 4)

        self.grid_layout.addWidget(self.name_label, 2, 0)
        self.grid_layout.addWidget(self.name_field, 2, 1)

    def lookup_process(self):
        d = ItemSelectDialog(self)
        d.setFont(self.font())
        result = d.exec_()
        if result:
            self.itemSelected.emit(d.selected_id)
    
    def setFields(self, _id, _barcode, _name):
        self.id_field.setText(str(_id))
        self.lookup_field.setText(str(_barcode))
        self.name_field.setText(str(_name))

class ItemConfigWidget(QGroupBox):
    def __init__(self, font=None) -> None:
        super().__init__()
        
        if font is None:
            font = self.font()
        else:
            self.setFont(font)

        self.grid_layout = QGridLayout()

        total_width = 0

        self.entry_type_label: QLabel = QLabel()
        self.entry_type_label.setFont(font)
        self.entry_type_label.setText("Entry Type")
        font_metric = QFontMetrics(self.entry_type_label.font())
        width = font_metric.width(self.entry_type_label.text())
        self.entry_type_label.setMaximumWidth(width)
        self.entry_type_label.setMinimumWidth(width)
        total_width += width

        self.entry_type_dropdown: QComboBox = QComboBox()
        self.entry_type_dropdown.setFont(font)
        self.entry_type_dropdown.addItems(["Select Type...", "LIST", "ITEM"])
        font_metric = QFontMetrics(self.entry_type_dropdown.font())
        height = font_metric.height()
        self.entry_type_dropdown.setMinimumHeight(height)
        total_width += self.entry_type_dropdown.width()

        self.sub_type_label: QLabel = QLabel()
        self.sub_type_label.setFont(font)
        self.sub_type_label.setText("Subtype")
        font_metric = QFontMetrics(self.sub_type_label.font())
        width = font_metric.width(self.sub_type_label.text())
        height = font_metric.height()
        self.sub_type_label.setMaximumWidth(width)
        self.sub_type_label.setMinimumHeight(height)
        total_width += width

        self.sub_type_dropdown: QComboBox = QComboBox()
        self.sub_type_dropdown.setFont(font)
        self.sub_type_dropdown.addItems(['Select Subtype', 'FOOD', 'FOOD_PLU', 'MEDICINAL', 'OTHER'])
        font_metric = QFontMetrics(self.sub_type_dropdown.font())
        height = font_metric.height()
        self.sub_type_dropdown.setMinimumHeight(height)
        total_width += self.sub_type_dropdown.width()

        self.check_widget: QWidget = QWidget()
        self.check_grid: QGridLayout = QGridLayout()
        self.expires_checkbox: QCheckBox = QCheckBox()
        self.expires_checkbox.setFont(font)
        self.expires_checkbox.setText('Expires')
        total_width += self.expires_checkbox.width()

        self.ai_pickable_checkbox: QCheckBox = QCheckBox()
        self.ai_pickable_checkbox.setFont(font)
        self.ai_pickable_checkbox.setText('AI Pickable')
        total_width += self.ai_pickable_checkbox.width()


        self.check_grid.addWidget(self.expires_checkbox, 0, 0)
        self.check_grid.addWidget(self.ai_pickable_checkbox, 1, 0)

        self.check_widget.setLayout(self.check_grid)

        self.grid_layout.addWidget(self.entry_type_label, 0, 0)
        self.grid_layout.addWidget(self.entry_type_dropdown, 0, 1)
        self.grid_layout.addWidget(self.sub_type_label, 1, 0)
        self.grid_layout.addWidget(self.sub_type_dropdown, 1, 1)
        self.grid_layout.addWidget(self.check_widget, 0, 2, 2, 1)

        self.setLayout(self.grid_layout)
        self.setTitle("Item Configuration")

    def setFields(self, _entry_type, _subtype, _ai_pickable, _expires):
        self.entry_type_dropdown.setCurrentText(_entry_type)
        self.sub_type_dropdown.setCurrentText(_subtype)
        if _expires == "yes":
            self.expires_checkbox.setCheckState(True)
        if _ai_pickable == "TRUE":
            self.ai_pickable_checkbox.setCheckState(True)

class ListMachineGroup(QGroupBox):
    def __init__(self, title, font):
        super().__init__()
        self.setTitle(title)

        self.grid_layout: QGridLayout = QGridLayout()

        self.inner_list: QListWidget = QListWidget()
        self.inner_list.setFont(font)

        self.add_button: QPushButton = QPushButton()
        self.add_button.setFont(font)
        self.add_button.setText("Add")

        self.delete_button: QPushButton = QPushButton()
        self.delete_button.setFont(font)
        self.delete_button.setText("Delete")

        self.grid_layout.addWidget(self.inner_list, 0, 0, 3, 2)
        self.grid_layout.addWidget(self.add_button, 3, 0)
        self.grid_layout.addWidget(self.delete_button, 3, 1)

        self.setLayout(self.grid_layout)
        
    def setFields(self, _items: list):
        for _item in _items:
            item = QListWidgetItem()
            item.setText(_item)
            self.inner_list.addItem(item)

class ListsWidgets(QWidget):
    def __init__(self, font) -> None:
        super().__init__()


        self.main_horizontal_layout: QHBoxLayout = QHBoxLayout()
        self.categories_list: ListMachineGroup = ListMachineGroup("Categories", font)
        self.brands_list: ListMachineGroup = ListMachineGroup("Brands", font)

        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: red;")

        self.main_horizontal_layout.addWidget(self.categories_list)
        self.main_horizontal_layout.addWidget(self.brands_list)

        self.main_horizontal_layout.addWidget(self.frame, 2)
        self.main_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_horizontal_layout)

    def setFields(self, _categories, _brands):
        self.categories_list.setFields(_categories)
        self.brands_list.setFields(_brands)

class WhereUsedWidget(QWidget):
    def __init__(self, font) -> None:
        super().__init__()
        self.setFont(font)
        self.main_horizontal_widget: QHBoxLayout = QHBoxLayout()

        self.recipes = ListMachineGroup("Recipes", font)
        self.shopping_lists = ListMachineGroup("Shopping Lists", font)
        self.groups = ListMachineGroup("Groups", font)

        self.main_horizontal_widget.addWidget(self.recipes)
        self.main_horizontal_widget.addWidget(self.shopping_lists)
        self.main_horizontal_widget.addWidget(self.groups)

        self.setLayout(self.main_horizontal_widget)

    def setFields(self, _recipes, _shopping_lists, _groups):
        _recipes = set(_recipes)
        recipes = [database.fetch_recipe(_recipe_id)[1] for _recipe_id in _recipes]
        self.recipes.setFields(recipes)
        _shopping_lists = set(_shopping_lists)
        _shopping_lists = [database.fetch_shopping_list(_list_id)[1] for _list_id in _shopping_lists]
        self.shopping_lists.setFields(_shopping_lists)

        _groups = set(_groups)
        _groups = [database.fetch_group(_group_id)[1] for _group_id in _groups]
        self.groups.setFields(_groups)

class DataTabs(QTabWidget):
    def __init__(self, font) -> None:
        super().__init__()
        self.setFont(font)

        self.where_used = WhereUsedWidget(font)
        self.addTab(self.where_used, "Where Used")


    def setFields(self, inventory_item):
        self.where_used.setFields(
            _recipes=inventory_item[27],
            _shopping_lists=inventory_item[26],
            _groups=inventory_item[19]
        )

class MainBodyWidget(QWidget):
    def __init__(self, font=None) -> None:
        super().__init__()

        if font is None:
            font = self.font()
        else:
            self.setFont(font)

        self.main_vertical_layout: QVBoxLayout = QVBoxLayout()

        self.basic_info = BasicInfoWidget(font)
        self.basic_info.itemSelected.connect(self.loadItem)

        self.list_widget = ListsWidgets(font)

        self.tabs_widget = DataTabs(font)

        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.addWidget(self.basic_info)
        self.main_vertical_layout.addWidget(self.list_widget)
        self.main_vertical_layout.addWidget(self.tabs_widget)

        self.setLayout(self.main_vertical_layout)

    def loadItem(self, _id):
        item = database.fetch_pantry(_id)
        self.setFields(item)

    def setFields(self, item):
        self.basic_info.setFields(
            _id=item[0], 
            _barcode=item[1],
            _name=item[2],
            _entry_type=item[23],
            _subtype=item[24],
            _ai_pickable=item[21],
            _expires=item[22]
            )
        self.list_widget.setFields(
            _categories=item[5],
            _brands=item[4]
        )
        self.tabs_widget.setFields(item)

class InventoryMaintenanceWindow(QMdiSubWindow):
    closed = pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()

        font = QFont()
        font.setPixelSize(12)
        font.setFamily('segoe ui light')
        self.status_bar: QStatusBar = QStatusBar()
        self.main_widget = QWidget()
        
        self.main_vertical_layout = QVBoxLayout()
        # put toolbar
        self.main_toolbar: InventoryMainToolbar = InventoryMainToolbar("Main Toolbar")
        self.main_toolbar.installEventFilter(self)
        self.main_toolbar.buttonHovered.connect(self.show_status_message)
        
        # main horizontal
        self.main_horizontal_layout: QHBoxLayout = QHBoxLayout()
        # all other widgets lay within this layout
        self.body_widget: MainBodyWidget = MainBodyWidget(font)

        self.main_horizontal_layout.addWidget(self.body_widget)

        self.main_vertical_layout.addWidget(self.main_toolbar)
        self.main_vertical_layout.addLayout(self.main_horizontal_layout)
        self.main_vertical_layout.addWidget(self.status_bar)
        self.main_widget.setLayout(self.main_vertical_layout)
        self.setWidget(self.main_widget)
        self.setWindowTitle("Inventory Maintenance")

    def closeEvent(self, event):
        self.closed.emit("inventory_maintenance_window")
        super().closeEvent(event)

    def show_status_message(self, message):
        self.status_bar.showMessage(message)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Leave:
            self.status_bar.clearMessage()
        return super().eventFilter(obj, event)