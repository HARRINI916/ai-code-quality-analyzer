from .tree_sitter_parser import NodeRules, TreeSitterLanguageParser


class GoParser(TreeSitterLanguageParser):
    def __init__(self):
        super().__init__(
            language="go",
            rules=NodeRules(
                function_tokens=("function_declaration", "method_declaration", "func_literal"),
                loop_tokens=("for_statement", "range_clause"),
                conditional_tokens=("if_statement", "switch_statement", "select_statement"),
            ),
        )
