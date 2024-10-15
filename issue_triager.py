import logging
from github import Github
import os
from dotenv import load_dotenv
from llm_utils import generate_command

load_dotenv()

def triage_issues(repo):
    logging.info(f"Triaging issues for repository {repo.name}")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        open_issues = repo.get_issues(state='open')
        
        for issue in open_issues:
            if not issue.labels:
                labels = suggest_labels(issue.title, issue.body)
                add_labels_to_issue(repo, issue, labels)
                
                priority = suggest_priority(issue.title, issue.body)
                add_priority_to_issue(repo, issue, priority)
                
                assignee = suggest_assignee(repo, issue.title, issue.body)
                if assignee:
                    issue.edit(assignee=assignee)
        
        logging.info(f"Finished triaging issues for {repo.name}")
    
    except Exception as e:
        logging.error(f"Error triaging issues for repository {repo.name}: {str(e)}")

def suggest_labels(title, body):
    prompt = f"""
    Suggest appropriate labels for the following GitHub issue:
    Title: {title}
    Body: {body}
    
    Provide a comma-separated list of labels. Choose from common labels like:
    bug, feature, documentation, help wanted, good first issue, enhancement, question
    """
    
    response = generate_command(prompt)
    return [label.strip() for label in response.split(',')]

def add_labels_to_issue(repo, issue, labels):
    existing_labels = [label.name for label in repo.get_labels()]
    valid_labels = [label for label in labels if label in existing_labels]
    
    if valid_labels:
        issue.add_to_labels(*valid_labels)
        logging.info(f"Added labels {', '.join(valid_labels)} to issue #{issue.number} in {repo.name}")

def suggest_priority(title, body):
    prompt = f"""
    Suggest a priority level for the following GitHub issue:
    Title: {title}
    Body: {body}
    
    Choose one priority level from: low, medium, high, critical
    """
    
    return generate_command(prompt).strip().lower()

def add_priority_to_issue(repo, issue, priority):
    priority_label = f"priority: {priority}"
    
    if priority_label not in [label.name for label in issue.labels]:
        issue.add_to_labels(priority_label)
        logging.info(f"Added priority {priority} to issue #{issue.number} in {repo.name}")

def suggest_assignee(repo, title, body):
    contributors = list(repo.get_contributors())
    
    if not contributors:
        return None
    
    prompt = f"""
    Suggest the most appropriate assignee for the following GitHub issue:
    Title: {title}
    Body: {body}
    
    Choose from the following contributors:
    {', '.join([c.login for c in contributors])}
    
    Provide only the username of the suggested assignee.
    """
    
    suggested_assignee = generate_command(prompt).strip()
    
    if suggested_assignee in [c.login for c in contributors]:
        return suggested_assignee
    else:
        return None