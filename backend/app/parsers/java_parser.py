from .tree_sitter_parser import NodeRules, TreeSitterLanguageParser


class JavaParser(TreeSitterLanguageParser):
    def __init__(self):
        super().__init__(
            language="java",
            rules=NodeRules(
                function_tokens=("method_declaration", "constructor_declaration"),
                loop_tokens=("for_statement", "while_statement", "do_statement"),
                conditional_tokens=("if_statement", "switch_expression", "switch_block_statement_group"),
            ),
        )
