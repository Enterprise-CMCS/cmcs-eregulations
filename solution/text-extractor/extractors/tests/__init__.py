from extractors import Extractor


class FileComparisonMixin:
    def _test_file_type(self, file_type):
        extractor = Extractor.get_extractor(file_type)
        output = extractor.extract(f"extractors/tests/fixtures/{file_type}_sample.{file_type}")
        with open(f"extractors/tests/fixtures/{file_type}_expected.txt", "rb") as f:
            expected = f.read().decode()
        self.assertEqual(output, expected)
