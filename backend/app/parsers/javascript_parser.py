from .tree_sitter_parser import NodeRules, TreeSitterLanguageParser


class JavaScriptParser(TreeSitterLanguageParser):
    def __init__(self):
        super().__init__(
            language="javascript",
            rules=NodeRules(
                function_tokens=("function_declaration", "method_definition", "arrow_function"),
                loop_tokens=("for_statement", "while_statement", "do_statement"),
                conditional_tokens=("if_statement", "switch_statement", "conditional_expression"),
            ),
        )
