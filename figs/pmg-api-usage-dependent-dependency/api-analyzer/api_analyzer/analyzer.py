import ast
import json
import warnings
from collections import defaultdict
from pathlib import Path
from tempfile import NamedTemporaryFile


def _annotate_parents(tree: ast.AST) -> None:
    """Add `.parent` links so we can walk up the tree."""
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent


def _in_type_checking_block(node: ast.AST) -> bool:
    """Check if in an `if TYPE_CHECKING:` block."""
    while hasattr(node, "parent"):
        parent = node.parent
        if isinstance(parent, ast.If):
            if isinstance(parent.test, ast.Name) and parent.test.id == "TYPE_CHECKING":
                return True
        node = parent
    return False


class ApiAnalyzerPy(ast.NodeVisitor):
    """API analyzer for .py file."""

    def __init__(self, package: str) -> None:
        self.package = package

        # alias map: local name → full path
        self.aliases: dict[str, str] = {}
        # usage counts
        self.usage: dict[str, int] = defaultdict(int)

    def visit_Import(self, node) -> None:
        if _in_type_checking_block(node):
            return
        for alias in node.names:
            if alias.name.startswith(self.package):
                asname = alias.asname or alias.name.split(".")[-1]
                self.aliases[asname] = alias.name

    def visit_ImportFrom(self, node) -> None:
        if _in_type_checking_block(node):
            return
        if node.module and node.module.startswith(self.package):
            for alias in node.names:
                asname = alias.asname or alias.name
                self.aliases[asname] = f"{node.module}.{alias.name}"

    def visit_Call(self, node) -> None:
        """Track function/method calls."""
        if isinstance(node.func, ast.Attribute):
            base = node.func.value
            if isinstance(base, ast.Name) and base.id in self.aliases:
                full = f"{self.aliases[base.id]}.{node.func.attr}"
                self.usage[full] += 1
        elif isinstance(node.func, ast.Name):
            if node.func.id in self.aliases:
                full = self.aliases[node.func.id]
                self.usage[full] += 1
        self.generic_visit(node)


def analyze_py(
    path: str | Path,
    package: str,
    ipynb_name: str | None = None,
) -> tuple[dict[str, str], dict[str, int]]:
    """
    Analyze a Python file for package API usage.

    Returns:
        aliases (dict): Mapping of local names → full package paths.
        usage (dict): Mapping of package API calls → count.
        ipynb_name (str): Used for tracking original name for ipynb file.
    """
    path = Path(path)

    if path.suffix != ".py":
        raise ValueError(f"cannot analyze non-py file: {path}")

    text = path.read_text(encoding="utf-8")

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="invalid escape sequence",  # from ipynb
            category=SyntaxWarning,
        )
        try:
            tree = ast.parse(text)
        except SyntaxError as e:
            path = ipynb_name or path  # overwrite with original ipynb name
            print(f"⚠️  Skipping {path} (AST parse error: {e})")
            return {}, {}

    _annotate_parents(tree)

    analyzer = ApiAnalyzerPy(package)
    analyzer.visit(tree)
    return analyzer.aliases, dict(analyzer.usage)


def analyze_notebook(
    path: str | Path, package: str
) -> tuple[dict[str, str], dict[str, int]]:
    """
    Analyze API usage of a Jupyter notebook (.ipynb).

    Args:
        path: Path to the .ipynb file.
        package: Package name to track (e.g., "numpy").

    Returns:
        aliases: Mapping of local alias -> fully qualified name
        usage: Mapping of API call -> usage count
    """

    def clean_notebook_code(code: str) -> str:
        """Remove Jupyter magics and shell commands."""
        cleaned: list[str] = []
        for line in code.splitlines():
            if not line or line.startswith(("!", "%", "?")):
                continue  # skip shell/magic/help commands
            cleaned.append(line)
        return "\n".join(cleaned)

    path = Path(path)
    if path.suffix != ".ipynb":
        raise ValueError(f"cannot analyze non-ipynb file: {path}")

    nb = json.loads(path.read_text(encoding="utf-8"))

    # Collect all code cells together into one big script
    combined_code_lines: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        code = "".join(cell.get("source", []))
        code = clean_notebook_code(code)
        if code.strip():
            combined_code_lines.append(code)
    combined_code = "\n\n".join(combined_code_lines)

    if not combined_code.strip():
        return {}, {}

    # Write full notebook code into one temp .py file
    with NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(combined_code)
        tmp_path = Path(tmp.name)

    # Analyze once, with full context
    aliases, usage = analyze_py(tmp_path, package, str(path))

    # Clean up
    tmp_path.unlink(missing_ok=True)

    return aliases, usage


def analyze_paths(
    paths: str | Path | list[str | Path],
    package: str,
    exclude: str | list[str] | None = None,
) -> tuple[dict[str, str], dict[str, int]]:
    """
    Analyze Python (.py) and Jupyter (.ipynb) files for API usage of `package`.

    Args:
        paths: a single file/dir path, or a list of them
        package: the package to analyze (e.g. "pymatgen")
        exclude: optional subdir name(s) to exclude, relative to each path
            e.g. exclude=["tests", "docs", ".venv"]

    Returns:
        aliases (dict): merged local → full package paths
        usage (dict): merged API usage counts across all files
    """
    if isinstance(paths, (str, Path)):
        paths = [paths]
    paths = [Path(p) for p in paths]

    if exclude is None:
        exclude = []
    elif isinstance(exclude, str):
        exclude = [exclude]
    exclude = set(exclude)

    all_aliases: dict[str, str] = {}
    all_usage: dict[str, int] = defaultdict(int)

    def should_skip(p: Path) -> bool:
        # skip hidden files/dirs
        if p.name.startswith("."):
            return True
        # skip if any parent directory matches an excluded subdir
        if any(parent.name in exclude for parent in p.parents):
            return True
        return False

    for path in paths:
        if not path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        if should_skip(path):
            continue

        if path.is_dir():
            candidates = path.rglob("*")
        else:
            candidates = [path]

        for f in candidates:
            if should_skip(f):
                continue
            if f.suffix == ".py":
                aliases, usage = analyze_py(f, package)
            elif f.suffix == ".ipynb":
                try:
                    aliases, usage = analyze_notebook(f, package)
                except Exception as e:
                    print(f"⚠️ Skipping {f} (error: {e})")
                    continue
            else:
                continue

            all_aliases.update(aliases)
            for k, v in usage.items():
                all_usage[k] += v

    return all_aliases, dict(all_usage)
