import logging
from github import Github
import os
from dotenv import load_dotenv
from llm_utils import generate_command

load_dotenv()

def review_code(repo, branch):
    logging.info(f"Reviewing code for repository {repo.name}")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        # Get all files in the repository
        files = repo.get_contents("", ref=branch)
        
        for file in files:
            if file.type == "file" and file.name.endswith((".py", ".js", ".html", ".css")):
                review_file(repo, file, branch)
        
        logging.info(f"Finished reviewing code for {repo.name}")
    
    except Exception as e:
        logging.error(f"Error reviewing code for repository {repo.name}: {str(e)}")

def review_file(repo, file, branch):
    content = file.decoded_content.decode()
    
    prompt = f"""
    Review the following code and provide feedback:
    File: {file.name}
    
    {content}
    
    Provide a concise code review focusing on:
    1. Code quality
    2. Best practices
    3. Potential bugs
    4. Performance improvements
    5. Security concerns
    
    Format your response as a bulleted list.
    """
    
    review = generate_command(prompt)
    
    if review.strip():
        create_review_comment(repo, file, review, branch)

def create_review_comment(repo, file, review, branch):
    try:
        commit = repo.get_branch(branch).commit
        repo.create_comment(
            commit.sha,
            f"AI Code Review for {file.path}:\n\n{review}",
            file.path,
            position=None
        )
        logging.info(f"Created code review comment for {file.path} in {repo.name}")
    except Exception as e:
        logging.error(f"Error creating code review comment for {file.path} in {repo.name}: {str(e)}")