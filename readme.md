# 路由协议的模拟过程 #



## 技术 ## 
python + PyQt5

`pipenv install` 

### 文件描述 ###
文件 | 描述
---- | -------
index.py | 入口，窗口、菜单、底部 等设置
node.py    |  路由节点
line.py   | 节点之前的连线
dock.py  | 窗口底部 dock，以及结果 table 

### 类 ###
类 | 描述
---- | -------
MainWindow | 主窗口，设置菜单、主组件、dock
MainWidget | 主组件, 直接右击，有菜单显示。可创建 路由节点
Node | 路由节点，名称是根据字幕顺序自动生成的，最多 26 * 26 个。在节点上右击，可以删除节点，连接相邻节点，距离为数字， 0 表示不联通
FormWidget| 右击路由节点，选择"连接"，后编辑记录的 表单
Line | 节点间的连线
DockWidget | 底部 dock
TableWidget | dock 内部用来展示数据的 table，可以拖动
