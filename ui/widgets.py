from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt


class CompactDraggableList(QtWidgets.QListWidget):
    """
    Compact draggable list widget with clean styling.
    Supports drag & drop reordering with visual feedback.
    """
    orderChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Enable internal drag & drop
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        
        # Clean, readable styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
                font-weight: 500;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 10px;
                margin: 3px 0;
                border-radius: 5px;
                background-color: #2b2b2b;
                border-left: 3px solid #444444;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
                border-left: 3px solid #14b8a6;
                color: #ffffff;
                font-weight: 600;
            }
            QListWidget::item:hover {
                background-color: #353535;
                border-left: 3px solid #666666;
            }
            QListWidget::item:selected:hover {
                background-color: #0e8489;
                border-left: 3px solid #1dd1bb;
            }
        """)
        
        # Spacing for visual clarity
        self.setSpacing(3)
        
        # Enable tooltips on hover
        self.setMouseTracking(True)

    def dropEvent(self, event):
        """Handle drop event and signal order change"""
        super().dropEvent(event)
        self.orderChanged.emit()

    def mouseMoveEvent(self, event):
        """Display tooltip with class details on hover"""
        super().mouseMoveEvent(event)
        item = self.itemAt(event.pos())
        if item:
            # Extract class name from numbered item text
            text = item.text()
            if '. ' in text:
                class_name = text.split('. ', 1)[1]
                position = self.row(item) + 1
                item.setToolTip(
                    f"<b>{class_name}</b><br>"
                    f"Position: {position}<br>"
                    f"<i>Drag to reorder</i>"
                )