class PathConverter:
    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class NumericConverter(PathConverter):
    regex = r'[\d]+'


class SubpartConverter(PathConverter):
    regex = r'[A-Za-z]-[A-Za-z]|[A-Za-z]'


class VersionConverter(PathConverter):
    regex = r'[\d\w]+-[\d\w]+(?:-\d+)?'


class AppendixConverter(PathConverter):
    # This will match almost any appendix format by looking for
    # "Appendix" at the start, followed by anything that doesn't include a slash
    regex = r'Appendix[^/]+'

    def to_python(self, value):
        # Convert dash-separated URL format back to list
        parts = value.split('-')
        return parts

    def to_url(self, value):
        if isinstance(value, list):
            return '-'.join(value)
        return value
