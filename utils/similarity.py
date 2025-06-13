from difflib import SequenceMatcher

def compare_strings(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_matching_blocks(a, b):
    matcher = SequenceMatcher(None, a, b)
    return matcher.get_matching_blocks()

def get_similarity_details(a, b):
    matcher = SequenceMatcher(None, a, b)
    similarity = matcher.ratio()
    matching_blocks = matcher.get_matching_blocks()
    matches = []

    for block in matching_blocks:
        if block.size > 10:  # skip very short matches
            match_text = a[block.a:block.a + block.size]
            matches.append(match_text.strip())

    return similarity, matches
