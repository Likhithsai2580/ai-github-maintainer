from litellm import completion
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def generate_command(prompt):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    model = os.getenv("LLM_MODEL", "llama2-70b-4096")

    if provider == "gemini":
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        content = response.text.strip()
    else:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv(f"{provider.upper()}_API_KEY")
        )
        content = response.choices[0].message.content.strip()
    
    return content

# ... (rest of the existing functions remain the same)

def generate_repository_update(repo_name, repo_content):
    prompt = f"""Analyze the following repository content for '{repo_name}' and suggest improvements:

{repo_content}

Provide specific suggestions for:
1. Code quality improvements
2. Performance optimizations
3. Security enhancements
4. New feature ideas
5. Documentation updates

For each suggestion, provide a brief explanation and, if applicable, a code snippet or example."""
    return generate_command(prompt)