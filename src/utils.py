import re


def stitch_across_pages(markdown_list, client, config):
    """利用纯文本LLM判断跨页内容是否应合并"""
    stitched = []
    prev = None

    for md in markdown_list:
        if "[ADVERTISEMENT" in md.upper():
            continue

        if prev and "[CONTINUED]" in prev and "[CONTINUATION]" in md:
            tail_match = re.search(r'([^.]*)\[CONTINUED\]', prev)
            head_match = re.search(r'\[CONTINUATION\]([^.]*)', md)
            if tail_match and head_match:
                tail = tail_match.group(1).strip()
                head = head_match.group(1).strip()

                check_prompt = (
                    f"判断以下两个片段是否属于同一句子，仅回答YES或NO。\n"
                    f"片段1: {tail}\n片段2: {head}"
                )
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": check_prompt}],
                    max_tokens=5
                )
                if "YES" in response.choices[0].message.content.upper():
                    prev = re.sub(r'\[CONTINUED\]', head, prev)
                    md = re.sub(r'\[CONTINUATION\]', '', md)
                else:
                    prev = prev.replace("[CONTINUED]", "")
                    md = md.replace("[CONTINUATION]", "")

        prev_clean = prev.replace("[CONTINUED]", "").replace("[CONTINUATION]", "") if prev else ""
        if prev_clean:
            stitched[-1] = prev_clean
        prev = md
        stitched.append(md)

    if prev:
        prev_clean = prev.replace("[CONTINUED]", "").replace("[CONTINUATION]", "")
        stitched[-1] = prev_clean

    return "\n\n".join(stitched)
