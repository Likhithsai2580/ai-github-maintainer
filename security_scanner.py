import logging
from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

def scan_repository(repo, branch):
    logging.info(f"Scanning repository {repo.name} for security vulnerabilities")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        # Get the repository's security vulnerabilities
        vulnerabilities = repo.get_vulnerability_alert()
        
        if vulnerabilities:
            report = "Security Vulnerabilities Found:\n\n"
            for vuln in vulnerabilities:
                report += f"- Package: {vuln.package.name}\n"
                report += f"  Severity: {vuln.severity}\n"
                report += f"  Description: {vuln.description}\n"
                report += f"  Fixed in version: {vuln.fixed_in}\n\n"
            
            # Create an issue with the vulnerability report
            repo.create_issue(
                title="Security Vulnerability Report",
                body=report,
                labels=["security", "vulnerability"]
            )
            logging.info(f"Created security vulnerability report for {repo.name}")
        else:
            logging.info(f"No security vulnerabilities found in {repo.name}")
    
    except Exception as e:
        logging.error(f"Error scanning repository {repo.name}: {str(e)}")

    # Perform additional custom security checks
    custom_security_checks(repo, branch)

def custom_security_checks(repo, branch):
    logging.info(f"Performing custom security checks for {repo.name}")
    
    try:
        # Check for hardcoded secrets
        secret_patterns = [
            "api_key",
            "secret_key",
            "password",
            "token"
        ]
        
        for content_file in repo.get_contents("", ref=branch):
            if content_file.type == "file":
                file_content = content_file.decoded_content.decode()
                for pattern in secret_patterns:
                    if pattern in file_content.lower():
                        create_security_issue(repo, content_file.path, pattern)
    
    except Exception as e:
        logging.error(f"Error performing custom security checks for {repo.name}: {str(e)}")

def create_security_issue(repo, file_path, pattern):
    issue_title = f"Potential security risk in {file_path}"
    issue_body = f"A potential security risk was detected in the file `{file_path}`.\n\n"
    issue_body += f"The following pattern was found: `{pattern}`\n\n"
    issue_body += "Please review this file and ensure no sensitive information is exposed."
    
    repo.create_issue(
        title=issue_title,
        body=issue_body,
        labels=["security", "needs review"]
    )
    logging.info(f"Created security issue for {file_path} in {repo.name}")