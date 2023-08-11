import ast
import isort
import re
import os


class ProjectDocsScanner:
    """
    Scanner to extract documentation from Python code
    """

    def __init__(self, project_path):
        """
        Initialize the scanner with the given project path
        """
        self.project_path = project_path

    def scan(self):
        """
        Scan all .py files in the project and extract docs in Markdown format
        """
        docs = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    docs.extend(self.extract_docs(file_path))

        return self.to_md(docs)

    def extract_docs(self, file_path):
        """
        Extract documentation from a single .py file
        Docs are returned as a list of dicts
        """
        with open(file_path, 'r') as f:
            code = f.read()

        tree = ast.parse(code)
        docs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func,
                                                                      ast.Name) and decorator.func.id == 'text_demo':
                        if isinstance(decorator.args[0], ast.Str):
                            title = decorator.args[0].s
                            explanation = decorator.args[1].s

                            code_start = node.lineno - 1
                            code_end = node.end_lineno
                            with open(file_path, 'r') as f:
                                code_lines = f.readlines()[code_start:code_end]
                                code = self.parse_code(code_lines)
                            docs.append({"title": title, "explanation": explanation, "code": code})
        return docs

    def parse_code(self, lines):
        """
        Parse and format the code segment
        Remove unnecessary code lines
        """
        code = [line for line in lines if not line.endswith("# HIDE")]
        while not code[0].strip().startswith('def') and not code[0].strip().startswith('async def'):
            del code[0]
        del code[0]
        if code[0].strip().startswith('"""'):
            while code[0].strip() != '"""':
                del code[0]
            del code[0]
        indentation = len(code[0]) - len(code[0].lstrip())
        code = [line[indentation:] for line in code]
        code = ['from nicegui import ui'] + [self.uncomment(line) for line in code]
        code = ['' if line == '#' else line for line in code]
        if not code[-1].startswith('ui.run('):
            code.append('')
            code.append('ui.run()')
        code = isort.code('\n'.join(code), no_sections=True, lines_after_imports=1)
        return code

    def to_md(self, docs):
        """
        Convert extracted docs to Markdown format
        """
        doc_str = ""
        for doc in docs:
            doc_str += f"## {doc['title']}\n\n"
            doc_str += f"Explanation: {doc['explanation']} \n\n"
            doc_str += f"**Code:**\n\n"
            doc_str += f"````python\n{doc['code']}\n````\n\n"
            doc_str += "*" * 40 + "\n\n"
        return doc_str

    def uncomment(self, text):
        UNCOMMENT_PATTERN = re.compile(r'^(\s*)# ?')
        """non-executed lines should be shown in the code examples"""
        return UNCOMMENT_PATTERN.sub(r'\1', text)


if __name__ == '__main__':
    # Set the local address for the nicegui project.
    ps = ProjectDocsScanner("xxx")
    doc = ps.scan()

    from embedding.embedding import EmbeddingLocalBackend

    em = EmbeddingLocalBackend("chroma")
    em.add_markdown_embedding(doc)
