class HasParent:
    def set_parent(self, parent):
        self.parent = parent

    def has_parent(self):
        return bool(self.parent)

    def parent(self):
        return self.parent
    