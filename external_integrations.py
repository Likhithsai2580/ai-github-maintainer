import logging
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def run_external_integrations(repo):
    logging.info(f"Running external integrations for repository {repo.name}")
    
    try:
        # Slack integration
        slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook_url:
            send_slack_notification(slack_webhook_url, repo)
        
        # Jira integration
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_api_token = os.getenv("JIRA_API_TOKEN")
        if jira_url and jira_username and jira_api_token:
            create_jira_issue(jira_url, jira_username, jira_api_token, repo)
        
        # Add more integrations here as needed
        
        logging.info(f"Finished running external integrations for {repo.name}")
    
    except Exception as e:
        logging.error(f"Error running external integrations for repository {repo.name}: {str(e)}")

def send_slack_notification(webhook_url, repo):
    message = f"AI Maintainer has processed repository: {repo.name}"
    payload = {"text": message}
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logging.info(f"Sent Slack notification for {repo.name}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending Slack notification for {repo.name}: {str(e)}")

def create_jira_issue(jira_url, username, api_token, repo):
    issue_data = {
        "fields": {
            "project": {"key": "AI"},  # Replace with your Jira project key
            "summary": f"AI Maintainer Report for {repo.name}",
            "description": f"AI Maintainer has processed the GitHub repository: {repo.name}",
            "issuetype": {"name": "Task"}
        }
    }
    
    auth = (username, api_token)
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{jira_url}/rest/api/2/issue", json=issue_data, auth=auth, headers=headers)
        response.raise_for_status()
        logging.info(f"Created Jira issue for {repo.name}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating Jira issue for {repo.name}: {str(e)}")