import xlrd

from .extractor import Extractor


class ExcelExtractor(Extractor):
    file_types = ("xls", "xlsx", "xlsm")

    def extract(self, file_path: str) -> str:
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
