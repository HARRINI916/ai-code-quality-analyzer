from ..parsers.base_parser import BaseParser
from ..parsers.c_parser import CParser
from ..parsers.cpp_parser import CppParser
from ..parsers.go_parser import GoParser
from ..parsers.java_parser import JavaParser
from ..parsers.javascript_parser import JavaScriptParser
from ..parsers.python_parser import PythonParser

PARSER_MAP: dict[str, type[BaseParser]] = {
    "python": PythonParser,
    "c": CParser,
    "cpp": CppParser,
    "java": JavaParser,
    "javascript": JavaScriptParser,
    "go": GoParser,
}


def extract_features(code: str, language: str) -> dict[str, float]:
    parser_cls = PARSER_MAP.get(language.lower())
    if parser_cls is None:
        supported = ", ".join(PARSER_MAP.keys())
        raise ValueError(f"Unsupported language '{language}'. Supported: {supported}.")

    parser = parser_cls()
    parsed = parser.parse(code)
    return parsed.to_features()
