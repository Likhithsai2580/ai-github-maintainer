from litellm import completion
import os
from dotenv import load_dotenv
import ollama

load_dotenv()

def generate_command(prompt):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    if provider == "ollama":
        response = ollama.generate(model=model, prompt=prompt)
        content = response['response'].strip()
    else:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv(f"{provider.upper()}_API_KEY")
        )
        content = response.choices[0].message.content.strip()
    
    # Wrap the content in a complete code block if it's a single function, class, or line
    if content.startswith(('def ', 'class ', 'import ', 'from ')) or '\n' not in content:
        content = f"```python\n{content}\n```"
    
    return content

def generate_feature_ideas(repo_name, repo_description, prompt):
    prompt = prompt.format(repo_name=repo_name, repo_description=repo_description)
    return generate_command(prompt)

def generate_test_cases(code):
    prompt = f"Generate test cases for the following code:\n\n{code}\n\nProvide the test cases in a format that can be easily implemented."
    return generate_command(prompt)

def generate_debug_suggestions(error_message, code):
    prompt = f"Debug the following code that produced this error: '{error_message}'\n\n{code}\n\nProvide suggestions to fix the issue."
    return generate_command(prompt)

def generate_code_optimization(code):
    prompt = f"Optimize the following code for better performance and readability:\n\n{code}\n\nProvide the optimized code."
    return generate_command(prompt)

def generate_code_review(code):
    prompt = f"Review the following code and provide suggestions for improvement:\n\n{code}\n\nProvide a detailed code review with specific suggestions."
    return generate_command(prompt)

def generate_documentation(code):
    prompt = f"Generate comprehensive documentation for the following code:\n\n{code}\n\nProvide detailed explanations for functions, classes, and important logic."
    return generate_command(prompt)

def generate_security_analysis(code):
    prompt = f"Perform a security analysis on the following code:\n\n{code}\n\nIdentify potential security vulnerabilities and suggest improvements."
    return generate_command(prompt)

def generate_performance_improvements(code):
    prompt = f"Analyze the following code for performance improvements:\n\n{code}\n\nProvide specific suggestions to enhance performance."
    return generate_command(prompt)

def generate_code_refactoring(code):
    prompt = f"Refactor the following code to improve its structure and maintainability:\n\n{code}\n\nProvide the refactored code with explanations."
    return generate_command(prompt)

def generate_api_documentation(code):
    prompt = f"Generate API documentation for the following code:\n\n{code}\n\nProvide a detailed API reference including endpoints, parameters, and responses."
    return generate_command(prompt)

def generate_dependency_update_suggestions(requirements):
    prompt = f"Analyze the following requirements.txt file and suggest updates:\n\n{requirements}\n\nProvide a list of packages that could be updated with their latest versions."
    return generate_command(prompt)

def generate_commit_message(changes):
    prompt = f"Generate a concise and informative commit message for the following changes:\n\n{changes}\n\nProvide a clear and descriptive commit message."
    return generate_command(prompt)

def generate_code_complexity_analysis(code):
    prompt = f"Analyze the following code for complexity:\n\n{code}\n\nProvide a complexity analysis including cyclomatic complexity, cognitive complexity, and suggestions for simplification."
    return generate_command(prompt)

def generate_code_style_suggestions(code):
    prompt = f"Review the following code for style improvements:\n\n{code}\n\nProvide suggestions to improve code style, readability, and adherence to best practices."
    return generate_command(prompt)

def generate_license_compliance_check(code):
    prompt = f"Check the following code for license compliance:\n\n{code}\n\nIdentify any potential license conflicts or issues with third-party libraries."
    return generate_command(prompt)

def generate_performance_profiling_suggestions(code):
    prompt = f"Analyze the following code for performance profiling:\n\n{code}\n\nProvide suggestions for performance profiling and potential bottlenecks to investigate."
    return generate_command(prompt)

def generate_pr_review(files):
    diffs = [f.patch for f in files]
    return generate_command(f"Review the following PR changes and provide feedback:\n\n{''.join(diffs)}")

def generate_code_explanation(code):
    return generate_command(f"Explain the following code in detail:\n\n{code}")