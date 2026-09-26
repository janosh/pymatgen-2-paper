import ast
import json
import warnings
from collections import Counter
from pathlib import Path


class ApiAnalyzerPy(ast.NodeVisitor):
    """API analyzer for .py file."""

    def __init__(self, package: str) -> None:
        self.package = package

        # alias map: local name → full path
        self.aliases: dict[str, str] = {}
        # usage counts
        self.usage: Counter[str] = Counter()
        # whether the visited node is nested in an `if TYPE_CHECKING:` block
        self.in_type_checking = False

    def visit_If(self, node: ast.If) -> None:
        """Skip imports nested anywhere in an `if TYPE_CHECKING:` block."""
        outer = self.in_type_checking
        self.in_type_checking = outer or (
            isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
        )
        self.generic_visit(node)
        self.in_type_checking = outer

    def visit_Import(self, node: ast.Import) -> None:
        """Record `import pkg.mod [as name]` aliases."""
        if self.in_type_checking:
            return
        for alias in node.names:
            if alias.name.startswith(self.package):
                asname = alias.asname or alias.name.split(".")[-1]
                self.aliases[asname] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Record `from pkg.mod import name [as alias]` aliases."""
        if self.in_type_checking:
            return
        if node.module and node.module.startswith(self.package):
            for alias in node.names:
                asname = alias.asname or alias.name
                self.aliases[asname] = f"{node.module}.{alias.name}"

    def visit_Call(self, node: ast.Call) -> None:
        """Track function/method calls."""
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id in self.aliases
        ):
            self.usage[f"{self.aliases[func.value.id]}.{func.attr}"] += 1
        elif isinstance(func, ast.Name) and func.id in self.aliases:
            self.usage[self.aliases[func.id]] += 1
        self.generic_visit(node)


def analyze_source(
    text: str, package: str, label: str | Path
) -> tuple[dict[str, str], dict[str, int]]:
    """Analyze Python source code for package API usage.

    Args:
        text: Python source code.
        package: Package name to track (e.g., "numpy").
        label: File name reported if the source fails to parse.

    Returns:
        aliases: Mapping of local names → full package paths.
        usage: Mapping of package API calls → count.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            # from analyzed foreign code, text differs across Python versions:
            # "invalid escape sequence '\\W'" (<=3.13) vs '"\\W" is an invalid ...'
            message=r".*invalid escape sequence",
            category=SyntaxWarning,
        )
        try:
            tree = ast.parse(text)
        except SyntaxError as e:
            print(f"⚠️  Skipping {label} (AST parse error: {e})")
            return {}, {}

    analyzer = ApiAnalyzerPy(package)
    analyzer.visit(tree)
    return analyzer.aliases, dict(analyzer.usage)


def analyze_py(path: str | Path, package: str) -> tuple[dict[str, str], dict[str, int]]:
    """Analyze a Python (.py) file for package API usage, see `analyze_source`."""
    path = Path(path)
    if path.suffix != ".py":
        raise ValueError(f"cannot analyze non-py file: {path}")
    return analyze_source(path.read_text(encoding="utf-8"), package, path)


def analyze_notebook(
    path: str | Path, package: str
) -> tuple[dict[str, str], dict[str, int]]:
    """Analyze a Jupyter notebook (.ipynb) for package API usage.

    All code cells are analyzed together as one script (minus Jupyter magics, shell
    and help commands) so aliases imported in one cell resolve in later cells.
    See `analyze_source` for the return values.
    """
    path = Path(path)
    if path.suffix != ".ipynb":
        raise ValueError(f"cannot analyze non-ipynb file: {path}")

    notebook = json.loads(path.read_text(encoding="utf-8"))
    cell_codes = (
        "\n".join(
            line
            for line in "".join(cell.get("source", [])).splitlines()
            # skip blank lines and shell/magic/help commands
            if line and not line.lstrip().startswith(("!", "%", "?"))
        )
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    )
    combined_code = "\n\n".join(code for code in cell_codes if code.strip())
    return analyze_source(combined_code, package, path)


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
    exclude_set = {exclude} if isinstance(exclude, str) else set(exclude or [])

    def should_skip(path: Path) -> bool:
        """Skip hidden files/dirs and anything below an excluded directory."""
        return path.name.startswith(".") or any(
            parent.name in exclude_set for parent in path.parents
        )

    all_aliases: dict[str, str] = {}
    all_usage: Counter[str] = Counter()
    for root in map(Path, paths):
        if not root.is_dir():
            raise NotADirectoryError(f"{root} is not a directory")
        if should_skip(root):
            continue

        for file in root.rglob("*"):
            if should_skip(file):
                continue
            if file.suffix == ".py":
                aliases, usage = analyze_py(file, package)
            elif file.suffix == ".ipynb":
                try:
                    aliases, usage = analyze_notebook(file, package)
                # malformed JSON, bad encoding or an unexpected notebook structure
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"⚠️ Skipping {file} (error: {e})")
                    continue
            else:
                continue

            all_aliases.update(aliases)
            all_usage.update(usage)

    return all_aliases, dict(all_usage)
