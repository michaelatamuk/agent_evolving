# Baseline skill — deliberately shallow.
# GAIA questions require multi-step real-world reasoning: looking up facts,
# chaining intermediate conclusions, and producing an exact short answer.
# The baseline gives a single-sentence guess without any structured reasoning.
#
# GEPA must discover that the expected behaviour requires:
#   1. Breaking the question into sub-questions
#   2. Reasoning through each step explicitly
#   3. Arriving at a single exact short answer (name, number, date, etc.)
#   4. NOT hedging with "I think" / "approximately" / "it depends"
#
# Expected baseline score  : ~0.10–0.25  (answer sometimes guessed correctly
#                             for easy Level 1 questions; wrong or vague otherwise)
# Expected evolved score   : ~0.40–0.60  (structured reasoning raises exact-match
#                             rate; tool-free ceiling is lower than the full benchmark)

SKILL_BODY = """\
You are a knowledgeable assistant. When given a question, answer it directly
and concisely in one or two sentences.

Provide only the final answer. Do not show your reasoning or list intermediate
steps that led to the answer.
"""
