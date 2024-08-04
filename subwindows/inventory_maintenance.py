from PyQt5.QtWidgets import (QMdiSubWindow, QStatusBar, QWidget, QVBoxLayout, QToolBar, QHBoxLayout, QAction, QGridLayout, QLineEdit,
                             QPushButton, QListWidget, QListWidgetItem, QLabel, QGroupBox, QFrame, QStyle, QDialog, QTreeWidgetItem, 
                             QTreeWidget, QComboBox, QCheckBox, QTabBar, QTabWidget)
from PyQt5.QtCore import pyqtSignal, QSize, QEvent, Qt
from PyQt5.QtGui import QFontMetrics, QFont
import database
from subwindows.InventoryItemSelect import ItemSelectDialog

class ClickableLListItem(QListWidgetItem):
    def __init__(self, item_id: int = None, inner_value: str = None):
        super().__init__()
        self.item_id = item_id
        self.inner_value = inner_value

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

class BasicInfoWidget(QWidget):
    itemSelected = pyqtSignal(int)
    itemUpdate = pyqtSignal(dict)

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
        self.lookup_group.itemUpdate.connect(self.update_item)
        
        self.config_group = ItemConfigWidget(font)
        self.config_group.itemUpdate.connect(self.update_item)

        self.sub_veritical_layout: QVBoxLayout = QVBoxLayout()
        self.sub_veritical_layout.addWidget(self.lookup_group)
        self.sub_veritical_layout.addWidget(self.config_group)

        self.categories_list = ListMachineGroup("Categories", font, editable=True)
        self.categories_list.itemUpdate.connect(self.update_item)

        self.filler_frame: QFrame = QFrame()
        self.filler_frame.setStyleSheet("background-color: blue;")

        self.main_horizontal_layout.addLayout(self.sub_veritical_layout)
        self.main_horizontal_layout.addWidget(self.categories_list)
        self.main_horizontal_layout.addWidget(self.filler_frame, 2)
        self.setLayout(self.main_horizontal_layout)
        self.main_horizontal_layout.setContentsMargins(0, 0, 0, 0)

    def lookup_process(self, _id):
        self.itemSelected.emit(_id)

    def setFields(self, _id, _name, _barcode, _brand, _entry_type, _subtype, _ai_pickable, _expires, _categories):
        self.lookup_group.setFields(_id, _barcode, _name, _brand)
        self.config_group.setFields(
            _entry_type,
            _subtype,
            _ai_pickable,
            _expires
        )
        self.categories_list.setFields(_categories)

    def update_item(self, data: dict) -> None:
        self.itemUpdate.emit(data)

class LookupGroup(QGroupBox):
    itemSelected = pyqtSignal(int)
    itemUpdate = pyqtSignal(dict)

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
        self.name_field.returnPressed.connect(self.update_name)

        self.name_label: QLabel = QLabel()
        self.name_label.setFont(font)
        self.name_label.setText("Name: ")
        font_metric = QFontMetrics(self.name_label.font())
        width = font_metric.width(self.name_label.text())
        self.name_label.setMaximumWidth(width)

        self.brand_field: QLineEdit = QLineEdit()
        self.brand_field.setFont(font)
        self.brand_field.setMinimumWidth(160)
        self.brand_field.returnPressed.connect(self.update_brand)

        self.brand_label: QLabel = QLabel()
        self.brand_label.setFont(font)
        self.brand_label.setText("Brand: ")
        font_metric = QFontMetrics(self.brand_label.font())
        width = font_metric.width(self.brand_label.text())
        self.brand_label.setMaximumWidth(width)

        self.grid_layout.addWidget(self.id_label, 0, 0)
        self.grid_layout.addWidget(self.id_field, 0, 1)

        self.grid_layout.addWidget(self.lookup_label, 1, 0)
        self.grid_layout.addWidget(self.lookup_field, 1, 1, 1, 2)
        self.grid_layout.addWidget(self.lookup_search, 1, 4)

        self.grid_layout.addWidget(self.name_label, 2, 0)
        self.grid_layout.addWidget(self.name_field, 2, 1)

        self.grid_layout.addWidget(self.brand_label, 3, 0)
        self.grid_layout.addWidget(self.brand_field, 3, 1)

        self.name_value = None
        self.brand_value = None

    def lookup_process(self):
        d = ItemSelectDialog(self)
        d.setFont(self.font())
        result = d.exec_()
        if result:
            self.itemSelected.emit(d.selected_id)
    
    def setFields(self, _id, _barcode, _name, _brand):
        self.name_value = _name
        self.brand_value = _brand
        self.id_field.setText(str(_id))
        self.lookup_field.setText(str(_barcode))
        self.name_field.setText(str(_name))
        self.brand_field.setText(str(_brand))

    def update_name(self):
        if self.name_value == self.name_field.text():
            return
        
        self.itemUpdate.emit({'name': self.name_field.text()})
    
    def update_brand(self):
        if self.brand_value == self.brand_field.text():
            return
        
        self.itemUpdate.emit({'brands': self.brand_field.text()})

class ItemConfigWidget(QGroupBox):
    itemUpdate = pyqtSignal(dict)

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
        self.entry_type_dropdown.currentTextChanged.connect(self.updateEntryType)

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
        self.sub_type_dropdown.currentTextChanged.connect(self.updateSubType)

        self.check_widget: QWidget = QWidget()
        self.check_grid: QGridLayout = QGridLayout()
        self.expires_checkbox: QCheckBox = QCheckBox()
        self.expires_checkbox.setFont(font)
        self.expires_checkbox.setText('Expires')
        total_width += self.expires_checkbox.width()
        self.expires_checkbox.clicked.connect(self.updateExpires)

        self.ai_pickable_checkbox: QCheckBox = QCheckBox()
        self.ai_pickable_checkbox.setFont(font)
        self.ai_pickable_checkbox.setText('AI Pickable')
        total_width += self.ai_pickable_checkbox.width()
        self.ai_pickable_checkbox.clicked.connect(self.updateAiPickable)


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
        self.entry_type = None
        self.subtype = None
        self.ai_pickable = None
        self.expires = None

    def setFields(self, _entry_type, _subtype, _ai_pickable, _expires):
        self.blockSignals(True)
        self.entry_type_dropdown.setCurrentText(_entry_type)
        self.sub_type_dropdown.setCurrentText(_subtype)
        if _expires == "yes":
            self.expires_checkbox.setCheckState(True)
        else:
            self.expires_checkbox.setCheckState(False)

        if _ai_pickable == "TRUE":
            self.ai_pickable_checkbox.setCheckState(True)
        else:
            self.ai_pickable_checkbox.setCheckState(False)

        self.blockSignals(False)
        self.entry_type = _entry_type
        self.subtype = _subtype
        self.ai_pickable = _ai_pickable
        self.expires = _expires

    def updateEntryType(self, newValue: str):
        if newValue == self.entry_type:
            return
        
        self.entry_type = newValue
        self.itemUpdate.emit({"entry_type": newValue})
    
    def updateSubType(self, newValue: str):
        if newValue == self.subtype:
            return
        
        self.entry_type = newValue
        self.itemUpdate.emit({"sub_type": newValue})

    def updateExpires(self, _expires):
        if _expires and self.expires != 'yes':
            self.itemUpdate.emit({'expires': 'yes'})
        
        elif not _expires and self.expires != 'no':
            self.itemUpdate.emit({'expires': 'no'})
        
    def updateAiPickable(self, _ai_pickable):
        if _ai_pickable and self.ai_pickable != 'yes':
            self.itemUpdate.emit({'AI_Pickable': 'yes'})
        
        elif not _ai_pickable and self.ai_pickable != 'no':
            self.itemUpdate.emit({'AI_Pickable': 'no'})


class ListMachineGroup(QGroupBox):
    itemUpdate = pyqtSignal(dict)
    
    def __init__(self, title, font, editable:bool=False):
        super().__init__()
        self.setTitle(title)

        self.grid_layout: QGridLayout = QGridLayout()

        self.inner_list: QListWidget = QListWidget()
        self.inner_list.setFont(font)
        self.inner_list.itemDelegate().closeEditor.connect(self.listEdited)

        self.selected_index = None
        self.list_input: QLineEdit = QLineEdit()
        self.list_input.setPlaceholderText("Category...")
        self.list_input.returnPressed.connect(self.add_item)

        self.add_button: QPushButton = QPushButton()
        self.add_button.setFont(font)
        self.add_button.setText("Add")
        self.add_button.clicked.connect(self.add_item)

        self.delete_button: QPushButton = QPushButton()
        self.delete_button.setFont(font)
        self.delete_button.setText("Delete")
        self.delete_button.clicked.connect(self.delete_item)

        self.grid_layout.addWidget(self.inner_list, 0, 0, 3, 2)
        self.grid_layout.addWidget(self.list_input, 3, 0, 1, 2)
        self.grid_layout.addWidget(self.add_button, 4, 0)
        self.grid_layout.addWidget(self.delete_button, 4, 1)

        self.setLayout(self.grid_layout)

        self.editable: bool = editable
        self.inner_items = []

    def add_item(self):
        self.list_input.setStyleSheet("")
        
        if self.list_input.text() == "":
            return
        
        if self.list_input.text() in self.inner_items:
            self.list_input.setStyleSheet("QLineEdit { border: 1px solid red; }")
            return

        item: ClickableLListItem = ClickableLListItem(inner_value=self.list_input.text())
        item.setText(self.list_input.text())
        if self.editable:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.inner_list.addItem(item)
        self.list_input.clear()

        self.updateCategories()
    
    def delete_item(self):
        if self.inner_list.currentItem():
            item = self.inner_list.takeItem(self.inner_list.currentRow())
            del item

            self.updateCategories()

    def listEdited(self):
        edited_item: ClickableLListItem = self.inner_list.currentItem()
        if edited_item.inner_value == edited_item.text() or edited_item.text() in self.inner_items:
            return
        
        self.updateCategories()

    def setFields(self, _items: list):
        self.inner_list.clear()
        self.inner_items = _items
        for _item in _items:
            item = ClickableLListItem(inner_value=_item)
            item.setText(_item)
            if self.editable:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.inner_list.addItem(item)

    def updateCategories(self):
        new_list = set([self.inner_list.item(ind).text() for ind in range(self.inner_list.count())])
        if new_list == self.inner_items:
            return
        
        self.inner_items = new_list
        self.itemUpdate.emit({"categories": list(new_list)})

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
        self.basic_info.itemUpdate.connect(self.update_item)

        self.tabs_widget = DataTabs(font)

        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.main_vertical_layout.addWidget(self.basic_info)
        self.main_vertical_layout.addWidget(self.tabs_widget)

        self.setLayout(self.main_vertical_layout)

        self.selected_id = None

    def loadItem(self, _id):
        item = database.fetch_pantry(_id)
        self.selected_id = _id
        self.setFields(item)

    def setFields(self, item):
        self.basic_info.setFields(
            _id=item[0], 
            _barcode=item[1],
            _name=item[2],
            _brand=item[3],
            _entry_type=item[23],
            _subtype=item[24],
            _ai_pickable=item[21],
            _expires=item[22],
            _categories=item[5]
            )
        self.tabs_widget.setFields(item)
    
    def update_item(self, data):
        database.update_pantry(self.selected_id, data)

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