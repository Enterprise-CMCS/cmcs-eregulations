from .exceptions import ExtractorException as ExtractorException
from .exceptions import ExtractorInitException as ExtractorInitException
from .extractor import Extractor as Extractor

# Add your file extractors here to initialize them
from .pdf import PdfExtractor as PdfExtractor
from .text import TextExtractor as TextExtractor
from .word import WordExractor as WordExractor
