import os
from flask import Flask, request, jsonify
from github import Github
from github import GithubIntegration
import jwt
import time
import yaml
import logging
from concurrent.futures import ThreadPoolExecutor
from github_utils import (
    get_repo_issues, create_pull_request, update_changelog, 
    commit_changes, get_or_create_date_branch, get_repo_contributors,
    get_repo_languages, get_repo_commit_activity, create_issue, add_label_to_issue
)
from llm_utils import *
from plugin_manager import PluginManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Set up logging
logging.basicConfig(
    level=config["logging"]["level"],
    filename=config["logging"]["file"],
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize plugin manager
plugin_manager = PluginManager(config)

app = Flask(__name__)

# GitHub App credentials
app_id = os.getenv('GITHUB_APP_ID')
private_key = os.getenv('GITHUB_PRIVATE_KEY').encode()

def get_installation_access_token(installation_id):
    # Create a JWT for the GitHub App
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + (10 * 60),
        'iss': app_id
    }
    jwt_token = jwt.encode(payload, private_key, algorithm='RS256')

    # Get an installation access token
    git_integration = GithubIntegration(app_id, private_key)
    access_token = git_integration.get_access_token(installation_id).token
    return access_token

def process_repo(repo, installation_id):
    try:
        logging.info(f"Processing repository: {repo.name}")
        
        date_branch = get_or_create_date_branch(repo)
        
        # Generate feature ideas
        if config["features"]["feature_generation"]:
            feature_ideas = generate_feature_ideas(repo.name, repo.description, config["custom_prompts"]["feature_ideas"])
            logging.info(f"Feature ideas for {repo.name}:\n{feature_ideas}")
            
            # Implement a feature
            new_feature_code = extract_code_from_response(implement_feature(repo.name, feature_ideas))
            commit_message = generate_commit_message(f"New feature: {new_feature_code[:50]}...")
            commit_changes(repo, f"new_feature_{int(time.time())}.py", commit_message, new_feature_code, date_branch)
        
        # Process existing code
        for content_file in repo.get_contents("", ref=date_branch)[:config["maintenance"]["max_files_per_repo"]]:
            if content_file.name.endswith(".py"):
                file_content = content_file.decoded_content.decode()
                
                if config["features"]["code_optimization"]:
                    optimized_code = extract_code_from_response(optimize_code(file_content))
                    commit_changes(repo, content_file.path, "Optimize code", optimized_code, date_branch)
                
                if config["features"]["code_review"]:
                    code_review = generate_code_review(file_content)
                    create_issue(repo, f"Code review for {content_file.name}", code_review)
                
                if config["features"]["security_analysis"]:
                    security_analysis = generate_security_analysis(file_content)
                    create_issue(repo, f"Security analysis for {content_file.name}", security_analysis)
                
                if config["features"]["performance_profiling"]:
                    performance_suggestions = generate_performance_improvements(file_content)
                    create_issue(repo, f"Performance suggestions for {content_file.name}", performance_suggestions)
        
        # Handle open issues
        if config["features"]["issue_handling"]:
            issues = get_repo_issues(repo)[:config["maintenance"]["max_issues_per_repo"]]
            for issue in issues:
                solution = extract_code_from_response(generate_issue_solution(issue.title, issue.body))
                create_pull_request(repo, f"Fix for issue #{issue.number}", solution, date_branch, "main")
        
        # Update dependencies
        if config["features"]["dependency_updates"]:
            requirements = repo.get_contents("requirements.txt", ref=date_branch).decoded_content.decode()
            updated_requirements = generate_dependency_update_suggestions(requirements)
            commit_changes(repo, "requirements.txt", "Update dependencies", updated_requirements, date_branch)
        
        # Generate documentation
        if config["features"]["documentation_generation"]:
            for content_file in repo.get_contents("", ref=date_branch):
                if content_file.name.endswith(".py"):
                    documentation = generate_documentation(content_file.decoded_content.decode())
                    commit_changes(repo, f"{content_file.name.replace('.py', '_docs.md')}", "Add documentation", documentation, date_branch)
        
        # Run plugins
        plugin_results = plugin_manager.run_plugins(repo, date_branch)
        for result in plugin_results:
            create_issue(repo, f"Plugin result: {result['name']}", str(result['result']))

        # Update CHANGELOG.md
        changelog_update = generate_changelog_entry(repo.name)
        update_changelog(repo, changelog_update, date_branch)

        logging.info(f"Finished processing {repo.name}")
    except Exception as e:
        logging.error(f"Error processing {repo.name}: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Check if the event is a GitHub webhook
    github_event = request.headers.get('X-GitHub-Event')
    if not github_event:
        return jsonify({"error": "Not a GitHub webhook"}), 400

    # Get the webhook payload
    payload = request.json

    if github_event == "installation" and payload['action'] == "created":
        # New installation created
        installation_id = payload['installation']['id']
        access_token = get_installation_access_token(installation_id)
        g = Github(access_token)
        for repo in payload['repositories']:
            repo_obj = g.get_repo(repo['full_name'])
            process_repo(repo_obj, installation_id)
    elif github_event == "push":
        # Push event
        installation_id = payload['installation']['id']
        access_token = get_installation_access_token(installation_id)
        g = Github(access_token)
        repo = g.get_repo(payload['repository']['full_name'])
        process_repo(repo, installation_id)

    return jsonify({"message": "Webhook processed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)