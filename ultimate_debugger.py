import ast
import importlib
import os
import json
import builtins

BUILTIN_NAMES = set(dir(builtins))

class StaticCodeAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path, file_content):
        self.issues = []
        self.file_path = file_path
        self.file_lines = file_content.splitlines()
        self.used_names = set()
/        self.ticker_input_vars = {} # Tracks variables assigned from st.text_input
        self.defined_names = set()
        self.imported_aliases = {}
        self.imported_top_level_names = set()
        self.imported_modules_being_checked = set()
        self.scope_stack = [{'type': 'module', 'defined': set()}]

    def _add_issue(self, issue_type, title, description, goal, line_number, code_snippet=None):
        """Adds a structured issue to the list."""
        if code_snippet is None and line_number is not None:
            try:
                # Provide 3 lines of context
                start = max(0, line_number - 2)
                end = min(len(self.file_lines), line_number + 1)
                snippet_lines = self.file_lines[start:end]
                code_snippet = "\n".join(snippet_lines)
            except IndexError:
                code_snippet = "Could not retrieve code snippet."

        self.issues.append({
            "filePath": self.file_path,
            "lineNumber": line_number,
            "issueType": issue_type,
            "title": title,
            "description": description,
            "codeSnippet": code_snippet,
            "aiGoal": goal
        })

    def _is_defined_in_scope(self, name):
        """Check if a name is defined in the current or any parent scope."""
        for scope in reversed(self.scope_stack):
            if name in scope['defined']:
                return True
        return False

    def visit_Module(self, node):
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            imported_name = alias.name
            asname = alias.asname or imported_name.split('.')[0]

            self.imported_top_level_names.add(asname)
            self.scope_stack[-1]['defined'].add(asname)
            self.imported_modules_being_checked.add(imported_name.split('.')[0])
            self.imported_aliases[asname] = imported_name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module_name = node.module
        if module_name:
            self.imported_modules_being_checked.add(module_name.split('.')[0])

        for alias in node.names:
            imported_name_from_module = alias.name
            asname = alias.asname or imported_name_from_module

            self.imported_top_level_names.add(asname)
            self.scope_stack[-1]['defined'].add(asname)

            if module_name:
                self.imported_aliases[asname] = f"{module_name}.{imported_name_from_module}"
            else:
                self.imported_aliases[asname] = imported_name_from_module
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            # Check for potential NameError
            if not self._is_defined_in_scope(node.id) and node.id not in BUILTIN_NAMES:
                self._add_issue(
                    issue_type="Potential Bug",
                    title=f"Potential NameError: '{node.id}' may be used before assignment",
                    description=(
                        f"The name '{node.id}' is used here, but it does not appear to be defined in the current scope "
                        "or any parent scopes. This could lead to a NameError at runtime. Ensure it is defined "
                        "as a local variable, global variable, function parameter, or imported name before this line."
                    ),
                    goal="Verify that the variable is correctly defined before use. If it's a typo, correct the name. If it's missing, add its definition.",
                    line_number=node.lineno
                )
        elif isinstance(node.ctx, (ast.Store, ast.Del)):
            self.scope_stack[-1]['defined'].add(node.id)

        self.generic_visit(node)

    def _visit_function(self, node, func_type="Function"):
        # Add function name to the parent scope's defined names
        self.scope_stack[-1]['defined'].add(node.name)
        if self.scope_stack[-1]['type'] == 'module':
            self.defined_names.add(node.name)

        # Create a new scope for the function
        func_scope = {'type': 'function', 'defined': {arg.arg for arg in node.args.args}}
        func_scope['defined'].update({arg.arg for arg in node.args.kwonlyargs})
        if node.args.vararg:
            func_scope['defined'].add(node.args.vararg.arg)
        if node.args.kwarg:
            func_scope['defined'].add(node.args.kwarg.arg)

        self.scope_stack.append(func_scope)

        if len(node.body) > 60:
            self._add_issue(
                issue_type="Code Quality",
                title=f"{func_type} '{node.name}' is too long",
                description=f"The {func_type.lower()} '{node.name}' has {len(node.body)} lines, which can make it hard to read, test, and maintain.",
                goal="Refactor the function into smaller, more manageable sub-functions, each with a single responsibility.",
                line_number=node.lineno
            )
        if len(node.args.args) > 7:
            self._add_issue(
                issue_type="Code Quality",
                title=f"{func_type} '{node.name}' has too many arguments",
                description=f"The {func_type.lower()} '{node.name}' has {len(node.args.args)} arguments, which can make it difficult to call correctly.",
                goal="Refactor the parameters into a single configuration object, dictionary, or a `dataclasses.dataclass` for better organization and clarity.",
                line_number=node.lineno
            )

        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        self._visit_function(node, "Function")

    def visit_AsyncFunctionDef(self, node):
        self._visit_function(node, "Async Function")

    def visit_ClassDef(self, node):
        self.scope_stack[-1]['defined'].add(node.name)
        if self.scope_stack[-1]['type'] == 'module':
            self.defined_names.add(node.name)

        self.scope_stack.append({'type': 'class', 'defined': set()})
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node):
        # First, visit the value side to handle cases like `x = y` where y might be undefined
        self.visit(node.value)

        # Then, process the targets to mark them as defined
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.scope_stack[-1]['defined'].add(target.id)
                if self.scope_stack[-1]['type'] == 'module':
                    self.defined_names.add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.scope_stack[-1]['defined'].add(elt.id)
                        if self.scope_stack[-1]['type'] == 'module':
                            self.defined_names.add(elt.id)
        # Do not call generic_visit to avoid double-visiting

        # --- Ticker-specific check for input sanitization ---
        if (isinstance(node.value, ast.Call) and
                isinstance(node.value.func, ast.Attribute) and
                isinstance(node.value.func.value, ast.Name) and
                node.value.func.value.id == 'st' and
                node.value.func.attr == 'text_input'):

            # Check if the call is chained with .strip() or .upper()
            is_sanitized = False
            current_call = node.value
            while isinstance(current_call, ast.Call) and isinstance(current_call.func, ast.Attribute):
                if current_call.func.attr in ('strip', 'upper'):
                    is_sanitized = True
                    break
                # Move to the next object in the chain, e.g., from x.upper() to x
                current_call = current_call.func.value

            if not is_sanitized:
                self._add_issue(
                    issue_type="Enhancement",
                    title="Ticker input may lack sanitization",
                    description="The value from 'st.text_input' is used directly. User input can contain extra spaces or be in lowercase, which might cause data fetching to fail.",
                    goal="Sanitize the user input by chaining '.strip().upper()' to the 'st.text_input' call. For example: `ticker = st.text_input(...).strip().upper()`.",
                    line_number=node.lineno
                )
            # Store the variable name for other checks
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.ticker_input_vars[target.id] = node.lineno

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'exec':
            self._add_issue(
                issue_type="Security",
                title="Use of 'exec' is a security risk",
                description="The 'exec' function executes a string as Python code, which can be a major security vulnerability if the string comes from an external source. It also makes code harder to read and debug.",
                goal="Avoid using 'exec'. Refactor the code to use safer alternatives, such as function calls or data structures.",
                line_number=node.lineno
            )
        # Check for deprecated st.cache
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'cache':
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'st':
                self._add_issue(
                    issue_type="Deprecation",
                    title="Use of deprecated 'st.cache'",
                    description=(
                        "'st.cache' is deprecated and will be removed in a future version. It has been replaced by 'st.cache_data' for caching data "
                        "and 'st.cache_resource' for caching global resources like ML models or database connections."
                    ),
                    goal="Replace 'st.cache' with either 'st.cache_data' or 'st.cache_resource' based on the function's purpose. Use 'st.cache_data' for serializable data (dataframes, dicts) and 'st.cache_resource' for non-serializable objects.",
                    line_number=node.lineno
                )
        
        # --- Ticker-specific check for error handling ---
        is_data_fetch_call = False
        if isinstance(node.func, ast.Attribute):
            # Check for yf.download(ticker)
            if (isinstance(node.func.value, ast.Name) and node.func.value.id == 'yf' and node.func.attr == 'download'):
                is_data_fetch_call = True
            # Check for data = yf.Ticker(ticker)
            if (isinstance(node.func.value, ast.Name) and node.func.value.id == 'yf' and node.func.attr == 'Ticker'):
                 is_data_fetch_call = True

        if is_data_fetch_call:
            # Check if any argument is a tracked ticker variable and if the call is in a try block
            arg_is_ticker = any(isinstance(arg, ast.Name) and arg.id in self.ticker_input_vars for arg in node.args)
            if arg_is_ticker and not self._is_in_try_block(node):
                self._add_issue(
                    issue_type="Potential Bug",
                    title="Data fetching for ticker is not wrapped in a try-except block",
                    description="This data fetching call uses a user-provided ticker. If the ticker is invalid or the API fails, the app will crash. This can be prevented with error handling.",
                    goal="Wrap the data fetching call in a `try...except` block to catch potential errors (like `IndexError`, `KeyError`, or network errors) and display a user-friendly message with `st.error()`.",
                    line_number=node.lineno
                )

        self.generic_visit(node)

    def check_unused_imports(self):
        """Checks for imported modules or names that are never used."""
        names_to_ignore = {
            'os', 'sys', 'ast', 'typing', 'streamlit', 'abc', 'collections',
            'logging', 're', 'datetime', 'json', 'pathlib', 'traceback',
            'subprocess', 'io', 'importlib', 'pstats', 'difflib'
        }

        # Special case: pandas and numpy are often imported as 'pd' and 'np' but might be used
        # implicitly by other libraries. It's safer to warn but with lower severity or ignore.
        # For this tool, we will ignore them to reduce noise.
        names_to_ignore.update(['pandas', 'numpy'])

        final_unused_imports = set()
        for imported_name in self.imported_top_level_names:
            if imported_name not in self.used_names:
                original_full_reference = self.imported_aliases.get(imported_name, imported_name)
                base_module_name = original_full_reference.split('.')[0]

                if base_module_name not in names_to_ignore:
                    final_unused_imports.add(imported_name)

        for name in sorted(list(final_unused_imports)):
            # Find the line number of the import
            line_num = None
            for i, line in enumerate(self.file_lines):
                if f"import {name}" in line or f"from .* import {name}" in line:
                    line_num = i + 1
                    break

            self._add_issue(
                issue_type="Code Quality",
                title=f"Unused import: '{name}'",
                description=f"The name '{name}' is imported but never used in the file. This adds unnecessary overhead and clutters the namespace.",
                goal=f"Remove the unused import for '{name}' to clean up the code.",
                line_number=line_num,
                code_snippet=self.file_lines[line_num-1] if line_num else f"import {name}"
            )

    def check_unused_definitions(self):
        """Checks for top-level functions, classes, and variables that are defined but never used."""
        names_to_ignore_definitions = {
            'main', 'test', 'setup', 'teardown', '_',
            '__all__', '__version__', '__author__', '__doc__',
            'unittest',
        }

        unused_definitions = self.defined_names - self.used_names - names_to_ignore_definitions

        for name in sorted(list(unused_definitions)):
            # Find the line number of the definition
            line_num = None
            for i, line in enumerate(self.file_lines):
                if line.strip().startswith(f"def {name}") or line.strip().startswith(f"class {name}"):
                    line_num = i + 1
                    break

            self._add_issue(
                issue_type="Code Quality",
                title=f"Unused definition: '{name}'",
                description=f"The top-level name '{name}' is defined but never used within the project. It might be dead code.",
                goal=f"Review '{name}'. If it is no longer needed, remove it to simplify the codebase. If it is intended for external use, consider adding it to an `__all__` list or ignoring this warning.",
                line_number=line_num
            )

    def check_dependencies(self):
        """Checks if top-level imported modules are installed."""
        std_lib = {
            'os', 'sys', 'ast', 'subprocess', 'pstats', 'io', 'importlib', 'pathlib',
            'json', 're', 'traceback', 'datetime', 'difflib', 'typing', 'collections',
            'math', 'time', 'functools', 'itertools', 'logging'
        }

        for module_name in self.imported_modules_being_checked:
            if module_name not in std_lib:
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    self._add_issue(
                        issue_type="Error",
                        title=f"Missing dependency: '{module_name}'",
                        description=f"The module '{module_name}' is imported but could not be found in the current environment. This will cause a ModuleNotFoundError at runtime.",
                        goal=f"Install the missing dependency, typically by running 'pip install {module_name}'. Also, ensure '{module_name}' is added to the 'requirements.txt' file.",
                        line_number=None,
                        code_snippet=f"import {module_name}  # Or similar 'from' import"
                    )

    def check_empty_ticker_validation(self):
        """Suggests validating the ticker input is not empty."""
        for var_name, line_num in self.ticker_input_vars.items():
            self._add_issue(
                issue_type="Enhancement",
                title=f"Consider validating if ticker '{var_name}' is empty",
                description=f"After getting the ticker input into '{var_name}', there is no explicit check to see if the user submitted an empty string. Processing an empty ticker will likely cause an error.",
                goal=f"Add a validation check immediately after the input is received, like `if not {var_name}: st.warning('Please enter a ticker symbol.')` and use `st.stop()` or `return` to halt execution.",
                line_number=line_num + 1 # Suggest adding it on the next line
            )

    def _is_in_try_block(self, node):
        """
        Walks up the AST from a given node to check if it's inside a Try block.
        This is a simplified check and might not cover all edge cases.
        """
        current = node
        while hasattr(current, 'parent'):
            if isinstance(current.parent, ast.Try):
                return True
            current = current.parent
        return False
def analyze_file(file_path):
    """Analyzes a single Python file and returns a list of issues."""
    print(f"Analyzing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=file_path)
        # Add parent pointers to each node for easier traversal up the tree
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        analyzer = StaticCodeAnalyzer(file_path, content)
        analyzer.visit(tree)

        # Run final checks after the tree has been fully visited
        analyzer.check_unused_imports()
        analyzer.check_unused_definitions()
        analyzer.check_empty_ticker_validation()
        analyzer.check_dependencies()
        return analyzer.issues
    except (SyntaxError, UnicodeDecodeError) as e:
        return [{
            "filePath": file_path,
            "lineNumber": getattr(e, 'lineno', 1),
            "issueType": "Fatal Error",
            "title": "Could not parse file due to Syntax Error",
            "description": f"The file could not be analyzed because it contains a syntax error: {e}",
            "codeSnippet": getattr(e, 'text', 'N/A'),
            "aiGoal": "Fix the Python syntax error in the file so it can be properly analyzed and executed."
        }]
    except Exception as e:
        return [{
            "filePath": file_path,
            "lineNumber": 1,
            "issueType": "Fatal Error",
            "title": "An unexpected error occurred during analysis",
            "description": f"An unexpected error occurred while analyzing this file: {e}",
            "codeSnippet": "",
            "aiGoal": "Investigate the debugger script or the target file for the cause of this unexpected analysis failure."
        }]

def main():
    """Main function to find all Python files and analyze them."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    all_issues = []
    
    print("========================================")
    print("  Ultimate Debugger - Static Analysis   ")
    print("========================================")
    print(f"Project root: {project_root}\n")

    for root, _, files in os.walk(project_root):
        # Skip virtual environments and other common non-project directories
        if any(d in root for d in ['.venv', 'venv', 'env', '__pycache__', '.git', '.streamlit']):
            continue

        for file in files:
            if file.endswith('.py') and file != os.path.basename(__file__):
                file_path = os.path.join(root, file)
                issues = analyze_file(file_path)
                if issues:
                    all_issues.extend(issues)

    print("\n========================================")
    print(f"  Analysis Complete. Found {len(all_issues)} issues.  ")
    print("========================================\n")

    if all_issues:
        # Pretty print the JSON output
        print(json.dumps(all_issues, indent=2))
    else:
        print("No issues found. Great job!")

if __name__ == "__main__":
    main()