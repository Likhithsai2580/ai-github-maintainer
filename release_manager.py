import logging
from github import Github
import os
from dotenv import load_dotenv
from semantic_version import Version
from llm_utils import generate_command

load_dotenv()

def manage_release(repo):
    logging.info(f"Managing release for repository {repo.name}")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        # Get the latest release
        latest_release = get_latest_release(repo)
        
        # Determine if a new release is needed
        if should_create_new_release(repo, latest_release):
            create_new_release(repo, latest_release)
        else:
            logging.info(f"No new release needed for {repo.name}")
    
    except Exception as e:
        logging.error(f"Error managing release for repository {repo.name}: {str(e)}")

def get_latest_release(repo):
    try:
        return repo.get_latest_release()
    except:
        return None

def should_create_new_release(repo, latest_release):
    if not latest_release:
        return True
    
    # Check for new commits since the last release
    last_release_date = latest_release.created_at
    new_commits = list(repo.get_commits(since=last_release_date))
    
    return len(new_commits) > 0

def create_new_release(repo, latest_release):
    new_version = get_new_version(latest_release)
    release_notes = generate_release_notes(repo, latest_release)
    
    repo.create_git_release(
        tag=new_version,
        name=f"Release {new_version}",
        message=release_notes,
        draft=False,
        prerelease=False
    )
    
    logging.info(f"Created new release {new_version} for {repo.name}")

def get_new_version(latest_release):
    if not latest_release:
        return "v0.1.0"
    
    current_version = Version(latest_release.tag_name.lstrip('v'))
    return f"v{current_version.next_patch()}"

def generate_release_notes(repo, latest_release):
    if latest_release:
        compare_url = f"{repo.html_url}/compare/{latest_release.tag_name}...main"
    else:
        compare_url = f"{repo.html_url}/commits/main"
    
    prompt = f"""
    Generate release notes for the following GitHub repository:
    Repository: {repo.name}
    Compare URL: {compare_url}
    
    Provide a concise summary of changes, including:
    1. New features
    2. Bug fixes
    3. Performance improvements
    4. Breaking changes (if any)
    
    Format the release notes in Markdown.
    """
    
    return generate_command(prompt)