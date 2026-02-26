from .tree_sitter_parser import NodeRules, TreeSitterLanguageParser


class CParser(TreeSitterLanguageParser):
    def __init__(self):
        super().__init__(
            language="c",
            rules=NodeRules(
                function_tokens=("function_definition",),
                loop_tokens=("for_statement", "while_statement", "do_statement"),
                conditional_tokens=("if_statement", "switch_statement", "case_statement"),
            ),
        )
