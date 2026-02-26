import ast


def parse_ast(code: str) -> ast.AST:
    try:
        return ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(f"Syntax error in submitted code: {exc.msg}") from exc
