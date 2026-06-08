from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path


LAYOUT_COMPONENTS = {"Layout", "LAYOUT"}
MENU_SPEC_COMPONENT_INDEX = 4
ROLE_PERMISSION_MODEL = "system.roles"
PERMISSION_MODEL = "system.permissions"


@dataclass(frozen=True)
class RouteComponentRef:
    """记录一个会生成动态路由的组件引用。"""

    source: str
    name: str
    component: str


def collect_view_components(repo_root: Path) -> set[str]:
    """收集前端真实存在的视图组件路径。"""
    views_root = repo_root / "frontend" / "src" / "views"
    return {
        view_file.relative_to(views_root).with_suffix("").as_posix()
        for view_file in views_root.rglob("*.vue")
    }


def read_python_assignment(path: Path, assignment_name: str):
    """读取 Python 文件中的字面量赋值，避免用字符串拼接猜测结构。"""
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == assignment_name for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"{path} 缺少 {assignment_name}")


def collect_fastapi_menu_specs(repo_root: Path) -> list[RouteComponentRef]:
    """收集 FastAPI 测试权限树中会绑定到角色的菜单组件。"""
    path = repo_root / "fastapi" / "tests" / "fixtures" / "permissions.py"
    specs = read_python_assignment(path, "MENU_SPECS")
    return [
        RouteComponentRef(str(path.relative_to(repo_root)), spec[0], spec[MENU_SPEC_COMPONENT_INDEX])
        for spec in specs
    ]


def collect_golden_fixture_routes(repo_root: Path) -> list[RouteComponentRef]:
    """收集 golden fixture 中角色可访问的菜单组件。"""
    path = repo_root / "fastapi" / "tests" / "test_import_django_data_golden.py"
    rows = read_python_assignment(path, "GOLDEN_FIXTURE_ROWS")
    return collect_role_bound_permission_components(repo_root, path, rows)


def collect_backend_init_routes(repo_root: Path) -> list[RouteComponentRef]:
    """收集 Django 初始化数据中默认角色可访问的菜单组件。"""
    path = repo_root / "backend" / "init_data.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return collect_role_bound_permission_components(repo_root, path, rows)


def collect_role_bound_permission_components(
    repo_root: Path, path: Path, rows: list[dict]
) -> list[RouteComponentRef]:
    """只校验默认角色实际绑定的权限，避免未分配的演示数据误伤动态路由契约。"""
    role_permission_ids = {
        permission_id
        for row in rows
        if row.get("model") == ROLE_PERMISSION_MODEL
        for permission_id in row.get("fields", {}).get("permissions", [])
    }
    return [
        RouteComponentRef(
            str(path.relative_to(repo_root)),
            str(row.get("pk")),
            str(row.get("fields", {}).get("component") or ""),
        )
        for row in rows
        if row.get("model") == PERMISSION_MODEL and row.get("pk") in role_permission_ids
    ]


def validate_refs(refs: list[RouteComponentRef], view_components: set[str]) -> list[str]:
    """校验动态路由组件路径存在且格式可被前端直接解析。"""
    errors: list[str] = []
    for ref in refs:
        component = ref.component.strip()
        if not component or component in LAYOUT_COMPONENTS:
            continue
        if component.startswith("/"):
            errors.append(f"{ref.source}:{ref.name} 组件路径不能以 / 开头: {component}")
            continue
        if component.endswith(".vue"):
            errors.append(f"{ref.source}:{ref.name} 组件路径不能带 .vue 后缀: {component}")
            continue
        if component not in view_components:
            errors.append(
                f"{ref.source}:{ref.name} 指向不存在的视图组件: "
                f"{component} -> frontend/src/views/{component}.vue"
            )
    return errors


def main(argv: list[str]) -> int:
    """执行动态路由组件契约校验。"""
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    view_components = collect_view_components(repo_root)
    refs = [
        *collect_fastapi_menu_specs(repo_root),
        *collect_golden_fixture_routes(repo_root),
        *collect_backend_init_routes(repo_root),
    ]
    errors = validate_refs(refs, view_components)
    if errors:
        print("动态路由组件契约校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"动态路由组件契约校验通过，共校验 {len(refs)} 个组件引用。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
