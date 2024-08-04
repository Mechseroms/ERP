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