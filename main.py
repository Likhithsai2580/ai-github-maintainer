import os
from github import Github
from dotenv import load_dotenv
import yaml
import logging
import schedule
from github_utils import (
    get_repo_issues, create_pull_request, update_changelog, 
    get_or_create_date_branch, get_repo_contributors,
    get_repo_languages, get_repo_commit_activity, create_issue
)
from llm_utils import generate_repository_update, generate_changelog_entry
from plugin_manager import PluginManager
from security_scanner import scan_repository
from performance_profiler import profile_repository
from dependency_updater import update_dependencies
from issue_triager import triage_issues
from code_reviewer import review_code
from release_manager import manage_release
from report_generator import generate_report
from external_integrations import run_external_integrations

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

# Initialize GitHub client
g = Github(os.getenv("GITHUB_TOKEN"))

# Initialize plugin manager
plugin_manager = PluginManager(config)

def process_repo(repo):
    logging.info(f"Processing repository: {repo.name}")
    
    try:
        date_branch = get_or_create_date_branch(repo)
        
        # Generate repository update suggestions
        repo_content = get_repository_content(repo, date_branch)
        update_suggestions = generate_repository_update(repo.name, repo_content)
        
        # Implement suggestions
        implement_suggestions(repo, update_suggestions, date_branch)
        
        # Run enhanced features
        scan_repository(repo, date_branch)
        profile_repository(repo, date_branch)
        update_dependencies(repo, date_branch)
        triage_issues(repo)
        review_code(repo, date_branch)
        manage_release(repo)
        
        # Run plugins
        plugin_results = plugin_manager.run_plugins(repo, date_branch)
        for result in plugin_results:
            create_issue(repo, f"Plugin result: {result['name']}", str(result['result']))

        # Update CHANGELOG.md
        changelog_update = generate_changelog_entry(repo.name)
        update_changelog(repo, changelog_update, date_branch)

        # Generate report
        report = generate_report(repo)
        create_issue(repo, "AI Maintainer Report", report)

        # Run external integrations
        run_external_integrations(repo)

        logging.info(f"Finished processing {repo.name}")
    except Exception as e:
        logging.error(f"Error processing repository {repo.name}: {str(e)}")

def get_repository_content(repo, branch):
    content = ""
    for content_file in repo.get_contents("", ref=branch):
        if content_file.type == "file" and content_file.name.endswith((".py", ".js", ".html", ".css")):
            content += f"File: {content_file.path}\n\n{content_file.decoded_content.decode()}\n\n"
    return content

def implement_suggestions(repo, suggestions, branch):
    # Parse suggestions and implement changes
    lines = suggestions.split("\n")
    current_file = None
    changes = {}
    
    for line in lines:
        if line.startswith("File:"):
            current_file = line.split(":")[1].strip()
            changes[current_file] = []
        elif current_file and line.strip():
            changes[current_file].append(line)
    
    for file, content in changes.items():
        if content:
            new_content = "\n".join(content)
            commit_message = f"Update {file} based on AI suggestions"
            try:
                contents = repo.get_contents(file, ref=branch)
                repo.update_file(file, commit_message, new_content, contents.sha, branch=branch)
            except:
                repo.create_file(file, commit_message, new_content, branch=branch)

def weekly_maintenance():
    logging.info("Starting weekly maintenance")
    user = g.get_user()
    for repo in user.get_repos()[:config["github"]["max_repos"]]:
        process_repo(repo)
    logging.info("Weekly maintenance completed")

def schedule_weekly_maintenance():
    schedule.every().week.do(weekly_maintenance)

if __name__ == "__main__":
    schedule_weekly_maintenance()
    while True:
        schedule.run_pending()
