import logging
from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QTableWidget, QScrollArea, \
    QTableWidgetItem, QHeaderView


class DockWidget(QDockWidget):
    """主窗口底部，显示状态"""

    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        self.table_Widget = TableWidget(self)
        self.init_ui()
        # self.show()

    def init_ui(self):
        self.setWidget(self.table_Widget)


class TableWidget(QScrollArea):
    """展示多个 table """

    def __init__(self, parent):
        super().__init__(parent)
        self.main_widget = parent.main_widget
        self.table = QTableWidget(self)

        self.init_ui()
        self.create_table()

    def init_ui(self):
        self.setWidget(self.table)

    def create_table(self):
        nodes = self.main_widget.nodes
        lines = self._count_lines()
        logging.info("create table")
        self._table(nodes, lines)

    def update_table(self, data):
        """进入计算模式之后，更新table
        """
        logging.info("update table")
        self._table(data.nodes, data.table)

    def _table(self, nodes, lines):
        table = self._new_table()
        # 因为 有些节点 是不可见的
        nodes = [n for n in nodes if n.isVisible()]
        count = len(nodes)
        table.setRowCount(count + 1)
        table.setColumnCount(3 * count)

        for i, node in enumerate(nodes):
            table.setSpan(0, i * 3, 1, 3)
            item = QTableWidgetItem(node.name)
            item.setTextAlignment(Qt.AlignHCenter)
            table.setItem(0, i * 3, item)
            for j, n in enumerate(nodes):
                if i == j:
                    continue
                ls = lines.get(node.name, {})
                table.setItem(j + 1, i * 3, QTableWidgetItem(' ' + n.name + " "))
                if n.name in ls and ls.get(n.name):
                    table.setItem(j + 1, i * 3 + 1, QTableWidgetItem(' ' + str(ls.get(n.name)[0]) + " "))
                    table.setItem(j + 1, i * 3 + 2, QTableWidgetItem(' ' + ls.get(n.name)[1] + " "))
        self.table = table
        self.setWidget(self.table)

    def _new_table(self):
        table = QTableWidget(self)
        table.setFixedHeight(200)
        table.setFixedWidth(1000)
        table.horizontalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        return table

    def _count_lines(self):
        """统计经过每一个节点的连线, 注意一根线连接两个节点"""
        lines = self.main_widget.lines
        table = defaultdict(dict)
        for l in lines:
            ns = l.nodes()
            table[ns[0]][ns[1]] = [l.distance, ns[1]]
            table[ns[1]][ns[0]] = [l.distance, ns[0]]
        return table
