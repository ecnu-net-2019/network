class Line:
    """路线"""

    def __init__(self, n1, n2, distance):
        self.n1 = n1
        self.n2 = n2
        self.distance = distance

    def connected(self, node):
        return self.n2 == node or self.n1 == node

    def end(self, node):
        if self.n1 == node:
            return self.n2
        elif self.n2 == node:
            return self.n1
        return None

    def nodes(self):
        return [self.n1, self.n2]

    def __str__(self):
        return "{}-{}({})".format(self.n1, self.n2, self.distance)
