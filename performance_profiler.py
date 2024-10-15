import logging
import os
from github import Github
from dotenv import load_dotenv
import cProfile
import pstats
import io

load_dotenv()

def profile_repository(repo, branch):
    logging.info(f"Profiling repository {repo.name}")
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    try:
        # Profile Python files
        profile_results = {}
        for content_file in repo.get_contents("", ref=branch):
            if content_file.name.endswith(".py"):
                profile_results[content_file.name] = profile_python_file(content_file.decoded_content.decode())
        
        # Generate profiling report
        report = generate_profiling_report(profile_results)
        
        # Create an issue with the profiling report
        repo.create_issue(
            title="Performance Profiling Report",
            body=report,
            labels=["performance", "profiling"]
        )
        logging.info(f"Created performance profiling report for {repo.name}")
    
    except Exception as e:
        logging.error(f"Error profiling repository {repo.name}: {str(e)}")

def profile_python_file(code):
    pr = cProfile.Profile()
    pr.enable()
    
    # Execute the code
    exec(code)
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    return s.getvalue()

def generate_profiling_report(profile_results):
    report = "Performance Profiling Report\n\n"
    
    for file_name, profile_data in profile_results.items():
        report += f"File: {file_name}\n"
        report += "=" * (len(file_name) + 6) + "\n\n"
        report += profile_data + "\n\n"
    
    report += "Recommendations:\n"
    report += "1. Review the functions with the highest cumulative time.\n"
    report += "2. Consider optimizing frequently called functions.\n"
    report += "3. Look for opportunities to reduce function call overhead.\n"
    report += "4. Investigate any unexpected time-consuming operations.\n"
    
    return report