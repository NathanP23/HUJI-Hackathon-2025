def generate_improvement_prompt(data: dict) -> str:
    """
    Given a dict with keys:
      - "original_question": str
      - "old answer": str
      - "strengths": List[str]
      - "weaknesses": List[str]
      - "names to answers": Dict[str, str]
    returns a single prompt string to:
      1) Critique each AI answer
      2) Improve the old answer
    """
    # Extract fields
    question    = data.get("original_question", "").strip()
    old_answer  = data.get("old answer", "").strip()
    strengths   = data.get("strengths", [])
    weaknesses  = data.get("weaknesses", [])
    names_ans   = data.get("names to answers", {})

    # Build prompt parts
    parts = []

    # 1. Original question
    parts.append(f"Original question:\n{question}\n")

    # 2. Aggregated strengths & weaknesses
    if strengths:
        parts.append("Aggregated strengths:\n" +
                     "\n".join(f"- {s}" for s in strengths) + "\n")
    if weaknesses:
        parts.append("Aggregated weaknesses:\n" +
                     "\n".join(f"- {w}" for w in weaknesses) + "\n")

    # 3. Critique each AI answer
    parts.append("For each of the following AI-generated answers, provide a concise, honest, and assertive critique, highlighting what works, what doesn't, and how it could be improved:\n")
    for name, answer in names_ans.items():
        parts.append(f"---\nAnswer by {name}:\n{answer}\n")

    # 4. Improve the old answer
    parts.append(
        "\n---\n"
        "Now, taking into account the critiques above, please rewrite and improve the previous answer below:\n"
        f"{old_answer}\n"
    )

    # Join all parts into one prompt string
    return "\n".join(parts)
