
class MetaData:

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __getattr__(self, key):
        return getattr(self, key)
