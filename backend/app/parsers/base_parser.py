from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ParsedCode:
    line_count: int
    number_of_loops: int
    nested_loop_depth: int
    number_of_functions: int
    number_of_conditionals: int
    cyclomatic_complexity: int
    comment_ratio: float

    def to_features(self) -> dict[str, float]:
        return {
            "line_count": float(self.line_count),
            "number_of_loops": float(self.number_of_loops),
            "nested_loop_depth": float(self.nested_loop_depth),
            "number_of_functions": float(self.number_of_functions),
            "number_of_conditionals": float(self.number_of_conditionals),
            "cyclomatic_complexity": float(self.cyclomatic_complexity),
            "comment_ratio": float(self.comment_ratio),
        }


class BaseParser(ABC):
    language: str

    @abstractmethod
    def parse(self, code: str) -> ParsedCode:
        raise NotImplementedError
