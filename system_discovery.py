"""
Static AST Codebase & Architecture Auditor
Analyzes the entire app directory without executing application code or loading DBs.
"""

import ast
import pathlib

APP_DIR = pathlib.Path("app")


class ArchitectureAuditor:
    def __init__(self, root_dir: pathlib.Path):
        self.root_dir = root_dir
        self.models = {}
        self.schemas = {}
        self.routers = {}
        self.services = {}

    def audit(self):
        print("\n=================== SYSTEM ARCHITECTURE AUDIT REPORT ===================")
        self._scan_directory()
        self._report_models()
        self._report_schemas()
        self._report_routers()
        self._report_services()
        print("=======================================================================\n")

    def _scan_directory(self):
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                self._analyze_file(py_file, tree)
            except Exception as e:
                print(f"❌ Failed to parse AST for {py_file}: {e}")

    def _analyze_file(self, path: pathlib.Path, tree: ast.AST):
        rel_path = path.relative_to(self.root_dir)
        folder = rel_path.parts[0] if len(rel_path.parts) > 1 else ""

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # SQLAlchemy Models
                if "models" in str(path):
                    cols = [
                        n.target.id
                        for n in ast.walk(node)
                        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
                    ]
                    self.models.setdefault(rel_path.name, []).append((node.name, cols))

                # Pydantic Schemas
                elif "schemas" in str(path):
                    fields = [
                        n.target.id
                        for n in ast.walk(node)
                        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
                    ]
                    self.schemas.setdefault(rel_path.name, []).append((node.name, fields))

                # Services
                elif "services" in str(path):
                    methods = [
                        n.name
                        for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and not n.name.startswith("_")
                    ]
                    self.services.setdefault(rel_path.name, []).append((node.name, methods))

            # FastAPI Endpoints in Routers
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and "routers" in str(path):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                        method = decorator.func.attr.upper()
                        if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                            path_val = "unknown"
                            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                path_val = decorator.args[0].value
                            self.routers.setdefault(rel_path.name, []).append(
                                (method, path_val, node.name)
                            )

    def _report_models(self):
        print("\n1. 🗄️  SQLAlchemy Models & Declared Attributes:")
        if not self.models:
            print("   (None found)")
        for file, classes in self.models.items():
            print(f"   📄 {file}:")
            for cls_name, cols in classes:
                cols_str = ", ".join(cols) if cols else "No annotations"
                print(f"      • {cls_name} -> [{cols_str}]")

    def _report_schemas(self):
        print("\n2. 📝 Pydantic Data Schemas:")
        if not self.schemas:
            print("   (None found)")
        for file, classes in self.schemas.items():
            print(f"   📄 {file}:")
            for cls_name, fields in classes:
                fields_str = ", ".join(fields) if fields else "No annotations"
                print(f"      • {cls_name} -> [{fields_str}]")

    def _report_routers(self):
        print("\n3. 🌐 API Router Endpoints:")
        if not self.routers:
            print("   (None found or all routers empty)")
        for file, endpoints in self.routers.items():
            print(f"   📄 {file}:")
            if not endpoints:
                print("      ⚠️  (File empty or no handlers declared)")
            for method, path_val, func_name in endpoints:
                print(f"      • {method:<6} {path_val:<25} -> {func_name}()")

    def _report_services(self):
        print("\n4. ⚙️  Service Layer Logic:")
        if not self.services:
            print("   (None found)")
        for file, classes in self.services.items():
            print(f"   📄 {file}:")
            for cls_name, methods in classes:
                methods_str = ", ".join(methods) if methods else "No public methods"
                print(f"      • {cls_name} -> [{methods_str}]")


if __name__ == "__main__":
    auditor = ArchitectureAuditor(APP_DIR)
    auditor.audit()
