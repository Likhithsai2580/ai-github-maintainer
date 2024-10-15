import logging
from github import Github
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import io
import base64

load_dotenv()

def generate_report(repo):
    logging.info(f"Generating report for repository {repo.name}")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        report = f"# AI Maintainer Report for {repo.name}\n\n"
        
        # Repository statistics
        report += "## Repository Statistics\n\n"
        report += f"- Stars: {repo.stargazers_count}\n"
        report += f"- Forks: {repo.forks_count}\n"
        report += f"- Open Issues: {repo.open_issues_count}\n"
        report += f"- Watchers: {repo.watchers_count}\n\n"
        
        # Commit activity
        report += "## Commit Activity\n\n"
        commit_activity = repo.get_stats_commit_activity()
        if commit_activity:
            weeks = [ca.week for ca in commit_activity]
            commits = [ca.total for ca in commit_activity]
            
            plt.figure(figsize=(10, 5))
            plt.plot(weeks, commits)
            plt.title("Commit Activity")
            plt.xlabel("Week")
            plt.ylabel("Number of Commits")
            
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            
            graph = base64.b64encode(img.getvalue()).decode()
            report += f"![Commit Activity](data:image/png;base64,{graph})\n\n"
        
        # Top contributors
        report += "## Top Contributors\n\n"
        contributors = repo.get_contributors()
        for contributor in list(contributors)[:5]:
            report += f"- {contributor.login}: {contributor.contributions} contributions\n"
        report += "\n"
        
        # Recent activity
        report += "## Recent Activity\n\n"
        recent_commits = repo.get_commits()[:5]
        for commit in recent_commits:
            report += f"- {commit.commit.message} (by {commit.commit.author.name})\n"
        report += "\n"
        
        # Language breakdown
        report += "## Language Breakdown\n\n"
        languages = repo.get_languages()
        total = sum(languages.values())
        for language, bytes in languages.items():
            percentage = (bytes / total) * 100
            report += f"- {language}: {percentage:.2f}%\n"
        
        logging.info(f"Generated report for {repo.name}")
        return report
    
    except Exception as e:
        logging.error(f"Error generating report for repository {repo.name}: {str(e)}")
        return f"Error generating report: {str(e)}"