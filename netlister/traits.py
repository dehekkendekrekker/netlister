class HasParent:
    def __init__(self) -> None:
        self.parent = None
        
    def set_parent(self, parent):
        self.parent = parent

    def has_parent(self):
        return bool(self.parent)

    def get_parent(self):
        return self.parent
