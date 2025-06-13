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

            file_contents1 = []
            file_contents2 = []

            file_map1 = {}  # maps code offset to filename for project 1
            file_map2 = {}  # maps code offset to filename for project 2

            offset1 = 0
            for path in data1["files"]:
                code = fetch_file_content(gl, int(id1), data1["branch"], path)
                file_contents1.append(code)
                file_map1.update({i: path for i in range(offset1, offset1 + len(code))})
                offset1 += len(code) + 1  # +1 for newline

            offset2 = 0
            for path in data2["files"]:
                code = fetch_file_content(gl, int(id2), data2["branch"], path)
                file_contents2.append(code)
                file_map2.update({i: path for i in range(offset2, offset2 + len(code))})
                offset2 += len(code) + 1

            full1 = "\n".join(file_contents1)
            full2 = "\n".join(file_contents2)

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

                        # get file names for each match
                        file1 = file_map1.get(block.a, "unknown")
                        file2 = file_map2.get(block.b, "unknown")

                        matches.append({
                            "file1": file1,
                            "code1": snippet1,
                            "file2": file2,
                            "code2": snippet2
                        })

            results.append({
                "pair": f"{data1['name']['project_name']} vs {data2['name']['project_name']}",
                "percentage": f"{percent}%",
                "matches": matches
            })

    return results
