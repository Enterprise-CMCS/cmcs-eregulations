class DisplayNameFieldMixin:
    @property
    def display_name(self):
        return str(self)
