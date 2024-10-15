from github import Github
import os
from datetime import datetime

def get_repo_issues(repo):
    return list(repo.get_issues(state='open'))

def create_pull_request(repo, title, body, head, base):
    return repo.create_pull(title=title, body=body, head=head, base=base)

def update_changelog(repo, new_content, branch):
    try:
        changelog = repo.get_contents("CHANGELOG.md", ref=branch)
        repo.update_file("CHANGELOG.md", "Update CHANGELOG.md", new_content, changelog.sha, branch=branch)
    except:
        repo.create_file("CHANGELOG.md", "Create CHANGELOG.md", new_content, branch=branch)

def commit_changes(repo, file_path, commit_message, content, branch):
    try:
        contents = repo.get_contents(file_path, ref=branch)
        repo.update_file(file_path, commit_message, content, contents.sha, branch=branch)
    except:
        repo.create_file(file_path, commit_message, content, branch=branch)

def create_branch(repo, branch_name):
    source = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)

def get_or_create_date_branch(repo):
    date_branch = f"update-{datetime.now().strftime('%Y-%m-%d')}"
    try:
        repo.get_branch(date_branch)
    except:
        create_branch(repo, date_branch)
    return date_branch

def get_repo_contributors(repo):
    return list(repo.get_contributors())

def get_repo_languages(repo):
    return repo.get_languages()

def get_repo_commit_activity(repo):
    return repo.get_stats_commit_activity()

def create_issue(repo, title, body):
    return repo.create_issue(title=title, body=body)

def add_label_to_issue(issue, label):
    issue.add_to_labels(label)