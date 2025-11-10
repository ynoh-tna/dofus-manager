from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt


class DraggableList(QtWidgets.QListWidget):
    """List with drag & drop reorder support and a simple style."""
    orderChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.orderChanged.emit()