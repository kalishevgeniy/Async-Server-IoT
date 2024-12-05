
class MetaData:

    def __setattr__(self, key, value):
        setattr(self, key, value)

    def __getattr__(self, key):
        return getattr(self, key)
