from openpyxl import load_workbook

from .extractor import Extractor


class ExcelExtractor(Extractor):
    file_types = ("xlsx", "xlsm")

    _valid_cell_types = ["s", "n", "b", "inlineStr", "str"]

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        output = ""

        # Open workbook read-only to avoid massive slowdown while iterating through cells
        workbook = load_workbook(file_path, read_only=True)
        for sheet in workbook:
            for row in sheet:
                for cell in row:
                    if cell.value and cell.data_type in self._valid_cell_types:
                        output += f" {str(cell.value)}"
        workbook.close()

        # Reopen workbook read-write so that the "_images" attribute is available
        workbook = load_workbook(file_path)
        for sheet in workbook:
            for i, image in enumerate(sheet._images):
                file_name = f"{sheet.title}_image{i}.{image.format}"
                output += f" {self._extract_embedded(file_name, image._data())}"
        workbook.close()

        return output
