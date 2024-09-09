from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import logging
from main import weekly_maintenance, process_repo
from github_utils import get_user_repos
import matplotlib.pyplot as plt
import io
import base64
import yaml

app = Flask(__name__)
socketio = SocketIO(app)

# Load configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trigger_maintenance', methods=['POST'])
def trigger_maintenance():
    threading.Thread(target=weekly_maintenance).start()
    return jsonify({"message": "Maintenance triggered successfully"})

@app.route('/process_repo', methods=['POST'])
def trigger_repo_process():
    repo_name = request.json.get('repo_name')
    repos = get_user_repos()[:config["github"]["max_repos"]]
    repo = next((r for r in repos if r.name == repo_name), None)
    if repo:
        threading.Thread(target=process_repo, args=(repo,)).start()
        return jsonify({"message": f"Processing repository: {repo_name}"})
    return jsonify({"error": f"Repository not found: {repo_name}"}), 404

@app.route('/logs')
def get_logs():
    try:
        with open(config["logging"]["file"], 'r') as log_file:
            logs = log_file.readlines()[-100:]  # Get last 100 lines
        return jsonify({"logs": logs})
    except Exception as e:
        logging.error(f"Error reading log file: {str(e)}")
        return jsonify({"error": "Unable to read log file"}), 500

@app.route('/generate_report')
def generate_report():
    try:
        repos = get_user_repos()[:config["github"]["max_repos"]]
        repo_names = [repo.name for repo in repos]
        commit_counts = [repo.get_commits().totalCount for repo in repos]

        plt.figure(figsize=(12, 6))
        plt.bar(repo_names, commit_counts)
        plt.title('Repository Commit Activity')
        plt.xlabel('Repositories')
        plt.ylabel('Number of Commits')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        
        return base64.b64encode(img.getvalue()).decode()
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        return jsonify({"error": "Unable to generate report"}), 500

@app.route('/repo_list')
def get_repo_list():
    try:
        repos = get_user_repos()[:config["github"]["max_repos"]]
        return jsonify({"repos": [repo.name for repo in repos]})
    except Exception as e:
        logging.error(f"Error fetching repository list: {str(e)}")
        return jsonify({"error": "Unable to fetch repository list"}), 500

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to server'})

@socketio.on('request_update')
def handle_update_request(data):
    repo_name = data.get('repo', 'all')
    if repo_name == 'all':
        emit('update', {'repo': 'all', 'status': 'Processing all repositories...'})
    else:
        emit('update', {'repo': repo_name, 'status': f'Processing repository: {repo_name}'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)