import radon.metrics as metrics
from radon.visitors import ComplexityVisitor

class Plugin:
    def run(self, repo, branch):
        results = {}
        for content_file in repo.get_contents("", ref=branch):
            if content_file.name.endswith(".py"):
                code = content_file.decoded_content.decode()
                mi = metrics.mi_visit(code, multi=True)
                cv = ComplexityVisitor.from_code(code)
                results[content_file.name] = {
                    "maintainability_index": mi,
                    "cyclomatic_complexity": cv.total_complexity,
                }
        return {
            "name": "Code Metrics",
            "result": results
        }