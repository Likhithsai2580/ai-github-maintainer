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
    
    return content

def extract_code_from_response(response):
    if response.startswith("```python") and response.endswith("```"):
        return response[10:-3].strip()
    return response

def generate_feature_ideas(repo_name, repo_description, prompt):
    prompt = prompt.format(repo_name=repo_name, repo_description=repo_description)
    return generate_command(prompt)

def implement_feature(repo_name, feature_ideas):
    prompt = f"""Implement one of the following feature ideas for the repository '{repo_name}':

{feature_ideas}

Provide a complete, production-ready implementation of the chosen feature. Include error handling, comments, and any necessary imports. The code should be well-structured and follow best practices."""
    return generate_command(prompt)

def optimize_code(code):
    prompt = f"""Optimize the following code for better performance and readability:

{code}

Provide the optimized code along with comments explaining the improvements made. Focus on:
1. Algorithmic efficiency
2. Memory usage
3. Code structure and organization
4. Adherence to PEP 8 style guide"""
    return generate_command(prompt)

def generate_code_review(code):
    prompt = f"""Perform a comprehensive code review for the following code:

{code}

Provide detailed feedback on:
1. Code quality and readability
2. Potential bugs or edge cases
3. Suggestions for improvement
4. Adherence to best practices and design patterns
5. Performance considerations"""
    return generate_command(prompt)

def generate_security_analysis(code):
    prompt = f"""Perform a security analysis on the following code:

{code}

Identify potential security vulnerabilities, including but not limited to:
1. Input validation issues
2. Authentication and authorization flaws
3. Data exposure risks
4. Injection vulnerabilities (SQL, command, etc.)
5. Insecure cryptographic storage
6. Insufficient error handling

Provide detailed explanations and suggestions for mitigation."""
    return generate_command(prompt)

def generate_performance_improvements(code):
    prompt = f"""Analyze the following code for performance improvements:

{code}

Provide specific suggestions to enhance performance, considering:
1. Time complexity optimization
2. Space complexity optimization
3. Caching strategies
4. Asynchronous processing opportunities
5. Database query optimization (if applicable)
6. Resource management and memory leaks"""
    return generate_command(prompt)

def generate_issue_solution(issue_title, issue_body):
    prompt = f"""Provide a solution for the following issue:

Title: {issue_title}
Description: {issue_body}

Generate a complete, production-ready solution that addresses the issue. Include:
1. A clear explanation of the problem
2. The proposed solution with code implementation
3. Any necessary tests or validation steps
4. Potential side effects or considerations"""
    return generate_command(prompt)

def generate_dependency_update_suggestions(requirements):
    prompt = f"""Analyze the following requirements.txt file and suggest updates:

{requirements}

Provide a list of packages that could be updated, including:
1. The current version
2. The latest stable version
3. Any breaking changes or important considerations for updating
4. Brief explanation of the benefits of updating each package"""
    return generate_command(prompt)

def generate_documentation(code):
    prompt = f"""Generate comprehensive documentation for the following code:

{code}

Provide detailed explanations for:
1. Overall purpose and functionality of the code
2. Each function, class, and important variable
3. Input parameters and return values
4. Any algorithms or complex logic used
5. Usage examples and potential edge cases
6. Any dependencies or requirements

The documentation should be clear, concise, and follow best practices for technical writing."""
    return generate_command(prompt)

def generate_commit_message(changes):
    prompt = f"""Generate a concise and informative commit message for the following changes:

{changes}

The commit message should:
1. Summarize the main changes in a brief title (50 characters or less)
2. Provide more details in the body, if necessary
3. Follow conventional commit message format (e.g., feat:, fix:, docs:, etc.)
4. Mention any breaking changes or important notes"""
    return generate_command(prompt)

def generate_changelog_entry(repo_name):
    prompt = f"""Generate a changelog entry for recent changes in the repository '{repo_name}'.

The changelog entry should:
1. Summarize the main features, improvements, and bug fixes
2. Be organized into sections (e.g., Added, Changed, Fixed)
3. Provide brief but informative descriptions of each change
4. Include any important notes or breaking changes
5. Follow a consistent format and style"""
    return generate_command(prompt)