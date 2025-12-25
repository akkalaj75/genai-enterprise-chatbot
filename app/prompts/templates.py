"""
Prompt templates for enterprise chatbot
"""

QA_PROMPT = """You are a helpful enterprise assistant. Answer the question based ONLY on the provided context. If the answer is not in the context, say "I don't have this information."

Context:
{context}

Question: {question}

Answer:"""

HALLUCINATION_CHECK_PROMPT = """Given the following response and source documents, identify any claims in the response that are NOT supported by the sources.

Response: {response}

Sources:
{sources}

Unsupported claims (if any):"""

SUMMARY_PROMPT = """Summarize the following enterprise document concisely in 3-4 sentences:

{document}

Summary:"""

ENTITY_EXTRACTION_PROMPT = """Extract key entities from the following policy document. Categories: NAMES, DATES, AMOUNTS, POLICIES.

Document:
{document}

Entities in JSON format:"""

CLASSIFICATION_PROMPT = """Classify the following question into one of these categories: POLICY, BENEFITS, TECHNICAL_ISSUE, OTHER.

Question: {question}

Category:"""
