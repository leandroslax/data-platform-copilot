import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.api.core.config import settings


def is_llm_configured() -> bool:
    return bool(settings.openai_api_key and settings.openai_response_model)


def synthesize_grounded_answer(question: str, contexts: list[dict]) -> str | None:
    if not is_llm_configured() or not contexts:
        return None

    grounding_chunks = []
    for context in contexts:
        if context.get("item_type") == "document":
            grounding_chunks.append(
                (
                    f"Document: {context.get('name') or context.get('item_id')}\n"
                    f"Path: {context.get('path') or 'n/a'}\n"
                    f"Summary: {context.get('description') or 'n/a'}"
                )
            )
        else:
            grounding_chunks.append(
                (
                    f"Dataset: {context['dataset_id']}\n"
                    f"Owner: {context.get('owner') or 'n/a'}\n"
                    f"Description: {context.get('description') or 'n/a'}\n"
                    f"Columns: {', '.join(column.get('name', '') for column in context.get('columns', [])[:12])}"
                )
            )

    grounding_text = "\n\n".join(grounding_chunks)

    payload = json.dumps(
        {
            "model": settings.openai_response_model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are a data platform copilot. Answer only from the provided context, "
                                "be concise, and explicitly mention when information is inferred."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Question: {question}\n\nGrounding context:\n{grounding_text}",
                        }
                    ],
                },
            ],
        }
    ).encode("utf-8")

    request = Request(
        f"{settings.openai_base_url.rstrip('/')}/responses",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None

    output_parts = []
    for item in body.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                output_parts.append(text)

    if output_parts:
        return "\n".join(output_parts).strip()

    output_text = body.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    return None
