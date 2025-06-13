from difflib import SequenceMatcher
from backend.gitlab_utils import fetch_file_content

def compare_similarity(gl, config):
    results = []
    if not gl:
        print("❌ GitLab not initialized.")
        return results

    items = list(config.items())

    for i in range(len(items)):
        id1, data1 = items[i]
        for j in range(i + 1, len(items)):
            id2, data2 = items[j]

            combined1 = []
            combined2 = []

            for path in data1["files"]:
                code = fetch_file_content(gl, int(id1), data1["branch"], path)
                combined1.append(code)

            for path in data2["files"]:
                code = fetch_file_content(gl, int(id2), data2["branch"], path)
                combined2.append(code)

            full1 = "\n".join(combined1)
            full2 = "\n".join(combined2)

            matcher = SequenceMatcher(None, full1, full2)
            percent = round(matcher.ratio() * 100, 2)

            blocks = matcher.get_matching_blocks()
            matches = []
            seen = set()

            for block in blocks:
                if block.size > 0:
                    snippet1 = full1[block.a:block.a + block.size].strip()
                    snippet2 = full2[block.b:block.b + block.size].strip()
                    if snippet1 and snippet1 not in seen:
                        seen.add(snippet1)
                        matches.append({
                            "code1": snippet1,
                            "code2": snippet2
                        })

            results.append({
                "pair": f"{data1['name']['project_name']} vs {data2['name']['project_name']}",
                "percentage": f"{percent}%",
                "matches": matches
            })

    return results
