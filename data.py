import logging
from collections import defaultdict


class Data:
    """开始计算"""

    def __init__(self, lines, nodes):
        """
        v_nodes 可用节点
        dict_lines[a][b] 表示 a、b 两点的距离,也是初始路由表
        nb_nodes 相邻节点
        routing_table 路由表
        :param lines:
        :param nodes: list<Node>
        """
        self.lines = lines
        self.nodes = nodes
        # self.dict_nodes = None
        self.v_nodes = None
        self.nb_nodes = None
        # self.dict_lines = None
        self.table = None
        self.stable = False
        self.history = []
        self.init_data()

    def init_data(self):
        v_nodes = [n.name for n in self.nodes if n.isVisible()]
        # dict_lines = defaultdict(dict)
        table = defaultdict(dict)
        nb_nodes = defaultdict(list)
        for l in self.lines:
            [a, b] = l.nodes()
            if a not in v_nodes or b not in v_nodes:
                continue
            table[a][b] = [l.distance, b]
            table[b][a] = [l.distance, a]
            nb_nodes[a].append(b)
            nb_nodes[b].append(a)
        # self.dict_lines = dict_lines
        self.v_nodes = v_nodes
        self.nb_nodes = nb_nodes
        self.table = table
        self.history.append(table)

    def next(self):
        """核心，算法，，就这么长。。。"""
        logging.info("next step calculation")
        table = self.table
        # 对于每一个节点 current node
        stable = True
        logging.info("old table: {}".format(self.table))
        for cn in self.v_nodes:
            # t = self.table.get(cn, {})
            # 每一个相邻节点 neighbor node
            for nb in self.nb_nodes.get(cn):
                # 这个节点当前路由表
                t = table.get(cn, {})
                # 获得此邻居的路由表
                nbt = self.table.get(nb)
                # 所有其他节点目标节点 destination node
                for dn in self.v_nodes:
                    if cn == dn:
                        continue
                    old_value = t.get(dn, [])
                    new_value_1 = t.get(nb)
                    new_value_2 = nbt.get(dn, [])

                    ov = int(old_value[0]) if old_value else -1
                    nv1 = int(new_value_1[0]) if new_value_1 else -1
                    nv2 = int(new_value_2[0]) if new_value_2 else -1

                    if not old_value and new_value_1 and new_value_2:
                        # 原路由表 没有数据，有路径有数据
                        stable = False
                        table[cn][dn] = [nv1 + nv2, nb]
                    elif old_value and new_value_1 and new_value_2 and ov > nv1 + nv2:
                        # 旧路径，新路径都有，但是新路径比较小
                        stable = False
                        table[cn][dn] = [nv1 + nv2, nb]
                    elif old_value:
                        # 有旧路径，没有新路径
                        table[cn][dn] = old_value
                    else:
                        # 新旧路径都没有
                        pass
        logging.info("new table: {}".format(table))
        self.history.append(table)
        self.stable = stable
        self.table = table
