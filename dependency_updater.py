import logging
import os
from github import Github
from dotenv import load_dotenv
import json
import requests

load_dotenv()

def update_dependencies(repo, branch):
    logging.info(f"Updating dependencies for repository {repo.name}")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        # Check for package.json (Node.js projects)
        package_json = get_file_content(repo, "package.json", branch)
        if package_json:
            update_nodejs_dependencies(repo, package_json, branch)
        
        # Check for requirements.txt (Python projects)
        requirements_txt = get_file_content(repo, "requirements.txt", branch)
        if requirements_txt:
            update_python_dependencies(repo, requirements_txt, branch)
        
        logging.info(f"Finished updating dependencies for {repo.name}")
    
    except Exception as e:
        logging.error(f"Error updating dependencies for repository {repo.name}: {str(e)}")

def get_file_content(repo, file_path, branch):
    try:
        file_content = repo.get_contents(file_path, ref=branch)
        return file_content.decoded_content.decode()
    except:
        return None

def update_nodejs_dependencies(repo, package_json, branch):
    data = json.loads(package_json)
    dependencies = data.get("dependencies", {})
    dev_dependencies = data.get("devDependencies", {})
    
    updated_deps = update_npm_dependencies(dependencies)
    updated_dev_deps = update_npm_dependencies(dev_dependencies)
    
    if updated_deps or updated_dev_deps:
        data["dependencies"] = updated_deps or dependencies
        data["devDependencies"] = updated_dev_deps or dev_dependencies
        updated_content = json.dumps(data, indent=2)
        
        commit_message = "Update Node.js dependencies"
        update_file(repo, "package.json", updated_content, commit_message, branch)

def update_npm_dependencies(dependencies):
    updated = {}
    for package, version in dependencies.items():
        latest_version = get_latest_npm_version(package)
        if latest_version and latest_version != version:
            updated[package] = latest_version
    return updated if updated else None

def get_latest_npm_version(package):
    try:
        response = requests.get(f"https://registry.npmjs.org/{package}/latest")
        data = response.json()
        return data.get("version")
    except:
        return None

def update_python_dependencies(repo, requirements_txt, branch):
    lines = requirements_txt.split("\n")
    updated_lines = []
    updated = False
    
    for line in lines:
        if "==" in line:
            package, version = line.split("==")
            latest_version = get_latest_pypi_version(package)
            if latest_version and latest_version != version:
                updated_lines.append(f"{package}=={latest_version}")
                updated = True
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    if updated:
        updated_content = "\n".join(updated_lines)
        commit_message = "Update Python dependencies"
        update_file(repo, "requirements.txt", updated_content, commit_message, branch)

def get_latest_pypi_version(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json")
        data = response.json()
        return data["info"]["version"]
    except:
        return None

def update_file(repo, file_path, content, commit_message, branch):
    try:
        contents = repo.get_contents(file_path, ref=branch)
        repo.update_file(file_path, commit_message, content, contents.sha, branch=branch)
        logging.info(f"Updated {file_path} in {repo.name}")
    except Exception as e:
        logging.error(f"Error updating {file_path} in {repo.name}: {str(e)}")