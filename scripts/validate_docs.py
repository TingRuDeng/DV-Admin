#!/usr/bin/env python3
import re
import sys
from pathlib import Path
AI_CONTEXT_PATH = Path("docs/AI_CONTEXT.md")
DEFAULT_PROFILE = "generic"
GENERIC_REQUIRED_FILES = ("AGENTS.md", "docs/README.md", "docs/AI_CONTEXT.md")
ANDROID_REQUIRED_FILES = ("docs/BUILD_MATRIX.md", "docs/MODULE_MAP.md", "docs/TESTING_MATRIX.md", "docs/MANIFEST_AND_PERMISSIONS.md")
MAX_FILE_BYTES = 1_000_000
MAX_AI_CONTEXT_LINES = 120
PLACEHOLDER_PATTERN = re.compile(r"\b(TBD|TODO|placeholder|fill in|later)\b|待补|待补充|后续补充")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_AUTHORITY_HEADINGS = ("## Purpose", "## Source of truth", "## Key facts", "## How to verify", "## Stale when")
LEGACY_AUTHORITY_HEADINGS = ("## Purpose", "## Source Of Truth", "## Key Facts", "## How To Verify", "## Stale When")
REQUIRED_AI_KEYS = ("purpose", "read_when", "source_of_truth", "verify_with", "stale_when")
AI_CONTEXT_SECTIONS = ("## Project Snapshot", "## Core Directories", "## Documentation Map", "## Common Task Reading Paths", "## High-Risk Areas", "## Validation Commands", "## Stale when")
GENERIC_SECTION_VALUES = {
    "tbd", "todo", "n/a", "coming soon", "run tests", "check manually",
    "follow best practices", "use proper architecture",
    "use clean architecture", "run appropriate tests", "follow conventions",
    "检查一下", "手动确认", "运行测试", "按需验证", "遵循最佳实践",
    "后续补充", "待补充", "人工检查", "执行测试", "使用合适的验证",
}
COMMAND_PREFIXES = ("./", "python", "python3", "gradle", "./gradlew", "npm", "pnpm", "yarn", "make", "git")
SKIPPED_DOC_PARTS = ("docs/archive/", "docs/AGENT_STARTER_PROMPT.md", "docs/DOC_SYNC_CHECKLIST.md")
SKIPPED_LINK_DIRS = {
    ".agents",
    ".codex",
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}
LEGACY_DOC_SECTION = "## Legacy detail docs"
def validate_root(root, profile=DEFAULT_PROFILE):
    base = Path(root).resolve()
    issues = validate_base(base)
    if issues:
        return issues
    issues.extend(validate_profile_files(base, profile))
    issues.extend(validate_authority_docs(base, legacy_detail_docs(base)))
    issues.extend(validate_ai_context(base))
    issues.extend(validate_links(base))
    return issues
def validate_base(base):
    if not base.exists():
        return [f"{base}: 路径不存在"]
    if not base.is_dir():
        return [f"{base}: 必须是目录"]
    return []
def validate_profile_files(base, profile):
    issues = []
    for rel in required_files_for(profile):
        if not (base / rel).exists():
            issues.append(f"{rel}: 缺少必需文件 {rel}")
    if profile not in ("generic", "android"):
        issues.append(f"{base}: 未知 profile {profile}")
    return issues
def required_files_for(profile):
    return GENERIC_REQUIRED_FILES + (ANDROID_REQUIRED_FILES if profile == "android" else ())
def validate_authority_docs(base, legacy_docs=()):
    issues = []
    for path in sorted((base / "docs").glob("*.md")):
        rel = relative_path(path, base)
        if should_skip_authority_doc(rel, legacy_docs):
            continue
        text = read_text(path)
        issues.extend(validate_file_text(path, base, text))
        if rel != AI_CONTEXT_PATH.as_posix():
            issues.extend(validate_authority_contract(path, base, text))
    return issues
def validate_file_text(path, base, text):
    rel = relative_path(path, base)
    issues = []
    if PLACEHOLDER_PATTERN.search(text):
        issues.append(f"{rel}: 存在占位词或未完成标记")
    if path.stat().st_size > MAX_FILE_BYTES:
        issues.append(f"{rel}: 文件超过 {MAX_FILE_BYTES} 字节")
    return issues
def validate_authority_contract(path, base, text):
    rel = relative_path(path, base)
    issues = []
    headings = authority_headings(text)
    if not headings:
        for heading in REQUIRED_AUTHORITY_HEADINGS:
            issues.append(f"{rel}: 缺少必备标题 {heading}")
    issues.extend(validate_ai_summary(rel, text, base))
    issues.extend(validate_generic_sections(rel, text, headings))
    return issues
def authority_headings(text):
    for headings in (REQUIRED_AUTHORITY_HEADINGS, LEGACY_AUTHORITY_HEADINGS):
        if all(heading in text for heading in headings):
            return headings
    return ()
def validate_ai_summary(rel, text, base):
    block = find_ai_summary_block(text)
    if not block:
        return [f"{rel}: 缺少 ai_summary 摘要块"]
    summary = parse_ai_summary(block)
    issues = []
    for key in REQUIRED_AI_KEYS:
        issues.extend(validate_summary_key(rel, key, summary))
    issues.extend(validate_source_paths(rel, summary, base))
    issues.extend(validate_verify_commands(rel, summary))
    return issues
def validate_summary_key(rel, key, summary):
    value = summary.get(key)
    if isinstance(value, list) and value:
        return []
    if isinstance(value, str) and value.strip():
        return []
    if key == "purpose":
        return [f"{rel}: ai_summary.purpose 不能为空"]
    return [f"{rel}: ai_summary.{key} 必须至少包含一项"]
def find_ai_summary_block(text):
    fenced = re.compile(r"```ya?ml\s+(ai_summary:.*?)```", re.DOTALL)
    fenced_match = fenced.search(text)
    if fenced_match:
        return fenced_match.group(1)
    frontmatter = re.compile(r"^---\s+(ai_summary:.*?)---", re.DOTALL)
    frontmatter_match = frontmatter.search(text)
    return frontmatter_match.group(1) if frontmatter_match else ""
def parse_ai_summary(block):
    data = {}
    current_key = ""
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line == "ai_summary:":
            continue
        if line.startswith("- ") and current_key:
            data.setdefault(current_key, []).append(clean_value(line[2:]))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = parse_scalar(value)
    return data
def parse_scalar(value):
    cleaned = clean_value(value)
    return [] if cleaned in ("", "[]") else cleaned
def clean_value(value):
    return value.strip().strip('"').strip("'")
def validate_ai_context(base):
    path = base / AI_CONTEXT_PATH
    if not path.exists():
        return []
    text = read_text(path)
    rel = AI_CONTEXT_PATH.as_posix()
    issues = validate_file_text(path, base, text)
    issues.extend(validate_ai_summary(rel, text, base))
    issues.extend(validate_ai_context_sections(rel, text))
    if len(text.splitlines()) > MAX_AI_CONTEXT_LINES:
        issues.append(f"{rel}: 超过 {MAX_AI_CONTEXT_LINES} 行上下文预算")
    return issues
def validate_ai_context_sections(rel, text):
    positions = []
    issues = []
    for section in AI_CONTEXT_SECTIONS:
        index = text.find(section)
        if index == -1:
            issues.append(f"{rel}: AI_CONTEXT 缺少章节 {section}")
        positions.append(index)
    known_positions = [position for position in positions if position >= 0]
    if known_positions != sorted(known_positions):
        issues.append(f"{rel}: AI_CONTEXT 章节顺序错误")
    return issues
def validate_source_paths(rel, summary, base):
    issues = []
    for entry in summary.get("source_of_truth", []):
        if should_check_path(entry) and not (base / entry).exists():
            issues.append(f"{rel}: source_of_truth 路径不存在 {entry}")
    return issues
def validate_verify_commands(rel, summary):
    issues = []
    for command in summary.get("verify_with", []):
        if not is_specific_command(command):
            issues.append(f"{rel}: verify_with 不是具体命令 {command}")
    return issues
def should_check_path(entry):
    if entry.startswith(("http://", "https://")):
        return False
    return "/" in entry or "." in Path(entry).name
def is_specific_command(command):
    lowered = command.strip().lower()
    if lowered in GENERIC_SECTION_VALUES:
        return False
    return lowered.startswith(COMMAND_PREFIXES)
def validate_generic_sections(rel, text, headings):
    issues = []
    for heading in headings:
        content = section_content(text, heading)
        if is_generic_section(content):
            issues.append(f"{rel}: 章节 {heading} 内容过于空泛")
    return issues
def section_content(text, heading):
    start = text.find(heading)
    if start == -1:
        return ""
    start += len(heading)
    match = re.search(r"\n## ", text[start:])
    end = start + match.start() if match else len(text)
    return text[start:end].strip()
def is_generic_section(content):
    normalized = re.sub(r"[`\s]+", " ", content).strip().lower()
    return normalized in GENERIC_SECTION_VALUES
def validate_links(base):
    issues = []
    for path in sorted(base.rglob("*.md")):
        if should_skip_link_doc(path, base):
            continue
        text = read_text(path)
        issues.extend(validate_links_in_file(path, base, text))
    return issues
def should_skip_link_doc(path, base):
    rel = relative_path(path, base)
    return rel.startswith("docs/archive/") or any(part in SKIPPED_LINK_DIRS for part in path.parts)
def validate_links_in_file(path, base, text):
    issues = []
    for target in LINK_PATTERN.findall(text):
        if is_external_or_anchor(target):
            continue
        target_path = (path.parent / target.split("#", 1)[0]).resolve()
        if not target_path.exists():
            rel = relative_path(path, base)
            issues.append(f"{rel}: 本地链接不存在 {target}")
    return issues
def should_skip_authority_doc(rel, legacy_docs=()):
    return rel in SKIPPED_DOC_PARTS or rel.startswith("docs/archive/") or rel in legacy_docs
def legacy_detail_docs(base):
    readme = base / "docs/README.md"
    if not readme.exists():
        return set()
    section = section_content(read_text(readme), LEGACY_DOC_SECTION)
    targets = LINK_PATTERN.findall(section)
    return {rel for target in targets if (rel := normalize_doc_target(target)).startswith("docs/")}
def normalize_doc_target(target):
    target = target.split("#", 1)[0]
    for prefix in ("../", "./"):
        if target.startswith(prefix):
            target = target[len(prefix):]
    return target if target.startswith("docs/") else f"docs/{target}"
def is_external_or_anchor(target):
    return target.startswith("#") or "://" in target or target.startswith("mailto:")
def read_text(path):
    return path.read_text(encoding="utf-8")
def relative_path(path, base):
    return path.resolve().relative_to(base).as_posix()
def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    root, profile = parse_args(args)
    issues = validate_root(root, profile=profile)
    for issue in issues:
        print(issue)
    return 1 if issues else 0
def parse_args(args):
    root = Path.cwd()
    profile = DEFAULT_PROFILE
    if args and not args[0].startswith("--"):
        root = Path(args[0])
        args = args[1:]
    index = 0
    while index < len(args):
        if args[index] == "--profile" and index + 1 < len(args):
            profile = args[index + 1]
            index += 2
            continue
        index += 1
    return root, profile
if __name__ == "__main__":
    raise SystemExit(main())
