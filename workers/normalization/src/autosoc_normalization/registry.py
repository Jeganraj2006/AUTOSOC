from typing import Dict, Type
from .parsers.base import BaseParser
import logging

logger = logging.getLogger(__name__)

class ParserRegistry:
    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}

    def register(self, source_type: str, parser: BaseParser):
        if source_type in self._parsers:
            logger.warning(f"Overwriting existing parser for source_type: {source_type}")
        self._parsers[source_type] = parser

    def get_parser(self, source_type: str) -> BaseParser:
        return self._parsers.get(source_type)

parser_registry = ParserRegistry()
