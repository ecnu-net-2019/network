import logging
import sys

from PyQt5.QtGui import QPainter, QKeySequence
from PyQt5.QtCore import Qt, QLineF
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, \
    QAction, QMainWindow, QMenu, QToolBar, QDockWidget

from data import Data
from dock import DockWidget
from node import get_node_name, Node


class Status:
    """
    当前状态，默认是 编辑 状态，点击 下一步/结果 进入 计算 状态
    编辑 状态 下，只记录节点和连线信息，不考虑相邻节点的信息
    计算 状态 下，每一步都是根据上一步的状态自动计算
    """
    OPT = "编辑"
    CAL = "计算"


class MainWidget(QWidget):
    """
    主窗口
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 所有节点
        self.nodes = []
        # 所有连接
        self.lines = []
        self.parent_widget = parent
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def contextMenuEvent(self, event):
        """"""
        logging.info("right click")
        menu = QMenu(self)

        # 添加新节点
        new_act = menu.addAction("新增节点")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == new_act:
            widget = self.new_node(event)
            self.parentWidget().layout().addWidget(widget)

    def new_node(self, event):
        """新增节点"""
        pos = event.pos()
        logging.info("new route node, location: {}".format(pos))
        name = get_node_name(len(self.nodes))
        widget = Node(name, pos, self)
        widget.move(pos)

        self.nodes.append(widget)
        self.parent_widget.init_dock()
        if self.parent_widget.status == Status.CAL:
            self.parent_widget.status = Status.OPT
            self.parent_widget.statusBar().showMessage(self.parent_widget.status)
        return widget

    def redraw(self):
        """每次更新节点之后就重新绘制连接图"""
        logging.info("redraw")
        self.parent_widget.init_dock()
        self.update()
        if self.parent_widget.status == Status.CAL:
            self.parent_widget.status = Status.OPT
            self.parent_widget.statusBar().showMessage(self.parent_widget.status)

    def paintEvent(self, e):
        """"""
        painter = QPainter()
        painter.begin(self)
        self.draw_lines(painter)
        painter.end()

    def draw_lines(self, painter):
        ns = {n.name: n.pos for n in self.nodes}
        for l in self.lines:
            nodes = l.nodes()
            s = ns.get(nodes[0])
            e = ns.get(nodes[1])
            # 保证从左到右绘制
            if s.x() > e.x():
                s, e = e, s
            sx, sy = s.x(), s.y()
            ex, ey = e.x(), e.y()
            # 找到中间店
            mx = (sx + ex) / 2
            my = (sy + ey) / 2
            painter.drawLine(QLineF(s.x() + 40, s.y(), e.x() + 15, e.y()))
            painter.drawText(int(mx), int(my), l.distance)


class MainWindow(QMainWindow):
    """"""

    def __init__(self):
        super().__init__()
        self.main_widget = MainWidget(self)
        self.dock_widget = None
        self.status = None
        self.data = None

        self.init_menu()
        self.init_ui()
        self.init_dock()
        self.init_status()
        self.setCentralWidget(self.main_widget)

        self.show()

    def init_menu(self):
        """初始化菜单"""
        # menubar = self.menuBar()
        # menu = menubar.addMenu('开始')

        # new_act = QAction('保存', self)
        # new_act.setShortcut('Ctrl+A')
        # exit_act = QAction('退出', self)
        # exit_act.setShortcut('Ctrl+Q')
        # exit_act.setStatusTip('退出应用')
        # menu.addActions([new_act])

        next_action = QAction('下一步', self)
        next_action.triggered.connect(self.next_)
        next_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))

        result_action = QAction('计算', self)
        result_action.triggered.connect(self.result)
        result_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))

        exit_action = QAction('退出', self)
        exit_action.triggered.connect(sys.exit)

        toolbar = QToolBar("Main Toolbar")
        toolbar.addActions([next_action, result_action, exit_action])
        self.addToolBar(toolbar)

    def init_ui(self):
        # 大小
        self.resize(1000, 800)
        # 居中
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('模拟路由协议')

    def init_dock(self):
        """底部展示 table"""
        # 删除原数据
        logging.info("init dock")
        if self.dock_widget:
            self.dock_widget.deleteLater()
        dw = DockWidget(self.main_widget)
        dw.setFeatures(QDockWidget.DockWidgetMovable)
        dw.setFeatures(QDockWidget.DockWidgetFloatable)
        dw.setFloating(True)
        self.dock_widget = dw
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_widget)

    def init_status(self):
        """最下面还有状态栏"""
        self.status = Status.OPT
        self.statusBar().showMessage(self.status)

    def next_(self):
        if self.status == Status.OPT:
            self.status = Status.CAL
            self.statusBar().showMessage(self.status)
            self.data = Data(self.main_widget.lines, self.main_widget.nodes)
        logging.info("click next")
        self.data.next()
        self.dock_widget.table_Widget.update_table(self.data)

    def result(self):
        if self.status == Status.OPT:
            self.status = Status.CAL
            self.statusBar().showMessage(self.status)
            self.data = Data(self.main_widget.lines, self.main_widget.nodes)
        logging.info("click result")
        while not self.data.stable:
            self.data.next()
        self.dock_widget.table_Widget.update_table(self.data)


def main():
    """"""
    logging.basicConfig(format="[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s", level=logging.DEBUG)
    logging.info("start")
    app = QApplication(sys.argv)
    m = MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
