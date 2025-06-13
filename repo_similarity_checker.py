import os
import gitlab
import time
import json
import logging
from dotenv import load_dotenv
from itertools import combinations
from utils.similarity import compare_strings

# Load env vars
load_dotenv()
GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

# Logging
log_file = f"data/logs/{time.strftime('%Y-%m-%d')}.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
print(f"🔍 Logging to {log_file}")

# Load config
with open("config/trainee_config.json") as f:
    CONFIG = json.load(f)

# GitLab connection
gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

# Create output folder
os.makedirs("output", exist_ok=True)

def fetch_file_content(project_id, file_path, branch):
    try:
        project = gl.projects.get(project_id)
        file_obj = project.files.get(file_path=file_path, ref=branch)
        return file_obj.decode().decode('utf-8')
    except Exception as e:
        logging.warning(f"❌ Could not read {file_path} from project {project_id}: {e}")
        return ""

def compare_and_report():
    report_lines = []
    comparison_data = []

    ids = list(CONFIG.keys())
    for id1, id2 in combinations(ids, 2):
        name1 = CONFIG[id1]["name"]
        name2 = CONFIG[id2]["name"]
        branch1 = CONFIG[id1]["branch"]
        branch2 = CONFIG[id2]["branch"]
        files1 = CONFIG[id1]["files"]
        files2 = CONFIG[id2]["files"]

        # Compare common files only
        common_files = set(files1) & set(files2)
        for file_path in common_files:
            content1 = fetch_file_content(id1, file_path, branch1)
            content2 = fetch_file_content(id2, file_path, branch2)

            if content1 and content2:
                similarity = compare_strings(content1, content2)
                if similarity > 0.1:
                    msg = f"⚠️ {name1} and {name2} have {similarity*100:.2f}% similarity in file: {file_path}"
                    print(msg)
                    logging.warning(msg)
                    comparison_data.append({
                        "trainee1": name1,
                        "trainee2": name2,
                        "file": file_path,
                        "similarity": similarity,
                        "code1": content1,
                        "code2": content2
                    })
                    report_lines.append(msg)

    # Save plain text report
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    report_path = f"output/similarity_report_{timestamp}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n✅ Report saved at: {report_path}")

    # Save detailed comparison
    detailed_path = f"output/detailed_comparison_{timestamp}.txt"
    with open(detailed_path, "w", encoding="utf-8") as f:
        for item in comparison_data:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"{item['trainee1']} vs {item['trainee2']} — File: {item['file']}\n")
            f.write(f"Similarity: {item['similarity']*100:.2f}%\n")
            f.write(f"\n--- {item['trainee1']} CODE ---\n{item['code1']}")
            f.write(f"\n--- {item['trainee2']} CODE ---\n{item['code2']}")
    print(f"📄 Detailed comparison saved at: {detailed_path}")

if __name__ == "__main__":
    compare_and_report()
