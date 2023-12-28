from extractors import Extractor


class FileComparisonMixin:
    BASE_PATH = "extractors/tests/fixtures/"
    
    def _test_file_type(self, file_type, **kwargs):
        variation = kwargs.get("variation", None)
        variation = f"{variation}_" if variation else ""
        config = kwargs.get("config", {})

        with open(f"{self.BASE_PATH}{file_type}/{variation}sample.{file_type}", "rb") as f:
            sample = f.read()
        with open(f"{self.BASE_PATH}{file_type}/{variation}expected.txt", "rb") as f:
            expected = f.read().decode()

        extractor = Extractor.get_extractor(file_type, config)
        output = extractor.extract(sample)
        self.assertEqual(output, expected)
