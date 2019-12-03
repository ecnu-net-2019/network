import logging
import os
import string

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMenu, QVBoxLayout, QLabel, QWidget, QPushButton, QScrollArea, QFormLayout, \
    QLineEdit

from line import Line


def get_node_name(num: int):
    """自动设置节点名称"""
    if num < 0:
        return ''
    if num < 26:
        return string.ascii_uppercase[num]
    else:
        a = num // 26
        b = num % 26
        return string.ascii_uppercase[a - 1] + string.ascii_uppercase[b]




class Node(QWidget):
    """
    节点设置
    """

    def __init__(self, name, pos, main_widget):
        """

        :param name: 名称
        :param pos: 位置
        :param main_widget: 主页面
        """
        super().__init__(parent=main_widget)
        self.name = name
        self.pos = pos
        self.main_widget = main_widget
        self.init_ui()

    def init_ui(self):
        node_label = QLabel()
        # 设置大小
        node_label.setGeometry(0, 0, 10, 10)
        # 设置图标
        pix = QPixmap(os.path.join(os.getcwd(), 'images/node.png'))
        node_label.setPixmap(pix)

        title = QLabel(self.name)
        title.setAlignment(Qt.AlignCenter)
        # 注意这里的新节点比较麻烦，
        # 使用 QVBoxLayout 组合 图标加文字，
        # QWidget 添加事件
        layout = QVBoxLayout()
        layout.addWidget(node_label)
        layout.addWidget(title)

        self.setGeometry(0, 0, 60, 70)
        self.setVisible(True)
        self.setLayout(layout)

    def contextMenuEvent(self, event):
        """操作节点"""
        logging.info("right click node")
        menu = QMenu(self)
        # 添加新节点
        line_act = menu.addAction("连接")
        delete_act = menu.addAction("删除")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == line_act:
            logging.info("set line")
            logging.info("current lines: {}".format([str(l) for l in self.main_widget.lines]))
            ls = FormWidget(self, self.main_widget.lines, self.main_widget.nodes)
            ls.move(self.pos.x() + 40, self.pos.y())
            self.main_widget.parentWidget().layout().addWidget(ls)

        elif action == delete_act:
            logging.info("remove node: {}".format(self.name))
            # 删除有连接的线
            lines = []
            for l in self.main_widget.lines:
                if not l.connected(self.name):
                    lines.append(l)
            self.main_widget.lines = lines
            logging.info("current lines: {}".format([str(n) for n in lines]))
            self.setVisible(False)
            self.main_widget.redraw()


class FormWidget(QScrollArea):
    """展示所有能连接的节点"""

    def __init__(self, current_node, lines, nodes):
        super().__init__()

        # 获取父组件（节点）信息
        self.current_node = current_node
        self.node_name = self.current_node.name
        self.lines = lines
        self.nodes = nodes
        self.values = {}

        self.init_ui()
        self.setGeometry(0, 0, 100, 150)

    def init_ui(self):
        widget = QWidget(self)
        layout = QFormLayout()
        layout.setAlignment(Qt.AlignTop)

        for n in self.nodes:
            # 排除自己和已经删除的节点
            if n.name == self.node_name or not n.isVisible():
                continue
            value = QLineEdit()
            # 是否已经连上
            v = 0
            for l in self.lines:
                if l.connected(n.name) and l.connected(self.node_name):
                    v = l.distance
                    break
            value.setText(str(v))
            value.setFixedWidth(50)
            layout.addRow(self.tr(n.name), value)
            self.values[n.name] = value
            logging.info("new box: {}".format(n.name))
        btn = QPushButton('完成', self)
        btn.clicked.connect(self.submit)
        layout.addWidget(btn)
        widget.setLayout(layout)
        self.setWidget(widget)

    def submit(self):
        """勾选完成之后，提交"""
        connect_node = []

        values = self.values
        for k, v in values.items():
            v = v.text()
            if v != '0' and v.isdigit():
                connect_node.append(Line(self.node_name, k, v))
        logging.info("node: {}, connect to :{}".format(self.node_name, [str(n) for n in connect_node]))
        lines = []
        for l in self.lines:
            # if self.node_name not in l:
            if not l.connected(self.node_name):
                lines.append(l)
        lines.extend(connect_node)
        logging.info("lines: {}".format([str(n) for n in lines]))
        self.current_node.main_widget.lines = lines
        self.deleteLater()
        self.current_node.main_widget.redraw()
