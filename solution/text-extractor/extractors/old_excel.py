import xlrd

from .extractor import Extractor


class OldExcelExtractor(Extractor):
    file_types = ("xls",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        workbook = xlrd.open_workbook(file_path)
        sheets = workbook.sheet_names()

        output = ""
        for sheet in sheets:
            worksheet = workbook.sheet_by_name(sheet)
            for i in range(worksheet.nrows):
                for j in range(worksheet.ncols):
                    value = worksheet.cell_value(i, j)
                    output += f" {str(value)}" if value else ""
        return output
