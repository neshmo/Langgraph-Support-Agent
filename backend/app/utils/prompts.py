"""
Centralized prompts for LLM calls.
"""

INTENT_CLASSIFICATION_PROMPT = """You are a support ticket classifier.

Analyze the following message and classify its intent.

Message:
{ticket_text}

You MUST respond with ONLY valid JSON in this exact format:
{{"intent": "<category>", "confidence": <0.0-1.0>}}

Valid intents: billing, technical, account, refund, general, complaint, off_topic

Rules:
- Return ONLY the JSON object, no markdown, no explanation
- Use "off_topic" for messages that are NOT customer support requests (greetings, casual chat, jokes, questions about AI, unrelated topics)
- confidence must be a number between 0.0 and 1.0
- If the message is clearly off-topic, use high confidence (0.9+)
- If unsure whether it's a support request, use lower confidence"""


# Prose prompt for streaming - returns readable text
SOLUTION_GENERATION_PROMPT_PROSE = """You are a senior customer support agent.

Customer Issue:
{ticket_text}

Detected Intent: {intent}

Relevant Knowledge:
{retrieved_docs}

Generate a helpful, step-by-step solution for the customer.

Rules:
- Respond with ONLY the solution text, no JSON, no metadata
- Number each step clearly (1., 2., 3., etc.)
- Keep the solution clear, actionable, and customer-friendly
- Do NOT include any JSON formatting or code blocks"""


# JSON prompt for non-streaming (backward compatibility)
SOLUTION_GENERATION_PROMPT = """You are a senior customer support agent.

Customer Issue:
{ticket_text}

Detected Intent: {intent}

Relevant Knowledge:
{retrieved_docs}

Generate a helpful solution for the customer.

You MUST respond with ONLY valid JSON in this exact format:
{{"solution": "<step-by-step solution>", "requires_followup": <true/false>}}

Rules:
- Return ONLY the JSON object, no markdown, no explanation
- Keep the solution clear and actionable
- Set requires_followup to true if the issue needs additional verification or actions"""


ESCALATION_REASON_PROMPT = """Explain briefly why this issue requires human intervention.

Ticket: {ticket_text}
Confidence: {confidence}

Respond in one sentence."""

