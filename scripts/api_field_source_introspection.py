from __future__ import annotations

import ast
from pathlib import Path


def resolve_dotted_source(root: Path, dotted_path: str) -> tuple[Path, tuple[str, ...]]:
    """把 dotted path 映射到源码文件和文件内符号链。"""
    parts = dotted_path.split(".")
    for index in range(len(parts) - 1, 0, -1):
        module_name = ".".join(parts[:index])
        source_path = module_path(root, module_name)
        if source_path.exists():
            return source_path, tuple(parts[index:])
    return module_path(root, ".".join(parts[:-1])), (parts[-1],)


def module_path(root: Path, module_name: str) -> Path:
    """将模块名转换为仓库内源码路径。"""
    if module_name.startswith("drf_admin."):
        return root / "backend" / Path(*module_name.split(".")).with_suffix(".py")
    if module_name.startswith("app."):
        return root / "fastapi" / Path(*module_name.split(".")).with_suffix(".py")
    return root / Path(*module_name.split(".")).with_suffix(".py")


def source_has_symbol(source_text: str, symbol_chain: tuple[str, ...]) -> bool:
    """校验源码中存在字段契约声明的类或函数符号。"""
    if not symbol_chain:
        return False
    tree = ast.parse(source_text)
    node = find_named_node(tree.body, symbol_chain[0])
    for symbol in symbol_chain[1:]:
        if not isinstance(node, ast.ClassDef):
            return False
        node = find_named_node(node.body, symbol)
    return node is not None


def extract_dict_output_keys(root: Path, dotted_path: str) -> set[str]:
    """从函数或方法内构造的响应 dict 中提取字符串字段名。"""
    source_path, symbol_chain = resolve_dotted_source(root, dotted_path)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    node = resolve_ast_node(tree, symbol_chain)
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set()
    keys: set[str] = set()
    for child in ast.walk(node):
        keys.update(assigned_dict_literal_keys(child))
        keys.update(returned_dict_literal_keys(child))
        keys.update(dict_subscript_assignment_keys(child))
    return keys


def resolve_ast_node(tree: ast.AST, symbol_chain: tuple[str, ...]) -> ast.AST | None:
    """按符号链定位 AST 节点。"""
    body = getattr(tree, "body", [])
    node = find_named_node(body, symbol_chain[0]) if symbol_chain else None
    for symbol in symbol_chain[1:]:
        body = getattr(node, "body", [])
        node = find_named_node(body, symbol)
    return node


def find_named_node(nodes: list[ast.stmt], name: str) -> ast.AST | None:
    """在同一层级查找指定名称的类或函数。"""
    for node in nodes:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def assigned_dict_literal_keys(node: ast.AST) -> set[str]:
    """提取直接赋值给变量的 dict 字面量 key。"""
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
        return dict_literal_keys(node.value)
    if isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Dict):
        return dict_literal_keys(node.value)
    return set()


def returned_dict_literal_keys(node: ast.AST) -> set[str]:
    """提取直接 return 的 dict 字面量 key。"""
    if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
        return set()
    return dict_literal_keys(node.value)


def dict_literal_keys(node: ast.Dict) -> set[str]:
    """提取单个 dict 字面量当前层级的字符串 key。"""
    return {key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}


def dict_subscript_assignment_keys(node: ast.AST) -> set[str]:
    """提取 `dict_obj["field"] = value` 形式的字符串 key。"""
    if not isinstance(node, ast.Assign):
        return set()
    keys: set[str] = set()
    for target in node.targets:
        if not isinstance(target, ast.Subscript):
            continue
        if isinstance(target.slice, ast.Constant) and isinstance(target.slice.value, str):
            keys.add(target.slice.value)
    return keys
