class PathConverter:
    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class NumericConverter(PathConverter):
    regex = r'[\d]+'


class SubpartConverter(PathConverter):
    regex = r'[A-Za-z]'


class VersionConverter(PathConverter):
    regex = r'[\d\w]+-[\d\w]+(?:-\d+)?'
