from utils.similarity import get_similarity_details
import logging

def compare_projects(proj1_name, proj1_files, proj2_name, proj2_files, report_file):
    for file1 in proj1_files:
        for file2 in proj2_files:
            if os.path.basename(file1['path']) == os.path.basename(file2['path']):
                content1 = file1['content']
                content2 = file2['content']
                similarity, matches = get_similarity_details(content1, content2)
                if similarity > 0.7:
                    log_msg = f"\n📄 MATCHED FILE: {file1['path']} ({similarity*100:.2f}%) between {proj1_name} and {proj2_name}\n"
                    log_msg += "-"*80 + "\n"
                    for m in matches:
                        log_msg += m + "\n" + "-"*80 + "\n"

                    print(log_msg)
                    logging.warning(log_msg)
                    with open(report_file, "a", encoding="utf-8") as f:
                        f.write(log_msg)
