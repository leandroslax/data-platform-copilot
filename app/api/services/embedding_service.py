import json
import math
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.api.core.config import settings

LOCAL_EMBEDDING_DIMENSION = 128


def _normalize_vector(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector
    return [value / magnitude for value in vector]


def _embed_locally(text: str) -> list[float]:
    vector = [0.0] * LOCAL_EMBEDDING_DIMENSION
    tokens = [token for token in text.lower().replace(".", " ").replace("_", " ").split() if token]
    counts = Counter(tokens)

    for token, count in counts.items():
        index = hash(token) % LOCAL_EMBEDDING_DIMENSION
        vector[index] += float(count)

    return _normalize_vector(vector)


def _embed_with_openai(text: str) -> list[float] | None:
    if not settings.openai_api_key:
        return None

    payload = json.dumps(
        {
            "model": settings.openai_embedding_model,
            "input": text,
        }
    ).encode("utf-8")
    request = Request(
        f"{settings.openai_base_url.rstrip('/')}/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None

    data = body.get("data") or []
    if not data:
        return None

    embedding = data[0].get("embedding")
    if not embedding:
        return None

    return _normalize_vector([float(value) for value in embedding])


def embed_text(text: str) -> list[float]:
    embedding = _embed_with_openai(text)
    if embedding is not None:
        return embedding

    return _embed_locally(text)
