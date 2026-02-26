from .tree_sitter_parser import NodeRules, TreeSitterLanguageParser


class PythonParser(TreeSitterLanguageParser):
    def __init__(self):
        super().__init__(
            language="python",
            rules=NodeRules(
                function_tokens=("function_definition", "lambda"),
                loop_tokens=("for_statement", "while_statement"),
                conditional_tokens=("if_statement", "elif_clause"),
            ),
        )
