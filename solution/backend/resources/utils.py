def is_int(x):
    try:
        _ = int(x)
        return True
    except ValueError:
        return False


class reverse_sort:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj
