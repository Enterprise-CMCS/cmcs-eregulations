from extractors import Extractor


class FileComparisonMixin:
    def _test_file_type(self, file_type, **kwargs):
        variation = kwargs.get("variation", None)
        variation = f"{variation}_" if variation else ""
        config = kwargs.get("config", {})

        extractor = Extractor.get_extractor(file_type, config)
        output = extractor.extract(f"extractors/tests/fixtures/{file_type}/{variation}sample.{file_type}")
        with open(f"extractors/tests/fixtures/{file_type}/{variation}expected.txt", "rb") as f:
            expected = f.read().decode()
        self.assertEqual(output, expected)
