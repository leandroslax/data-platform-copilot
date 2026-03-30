from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_chat_answers_orders_question() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"question": "Quem e o owner do dataset orders?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "main.sales.orders" in payload["answer"]
    assert len(payload["sources"]) == 2


def test_chat_answers_job_question() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"question": "Qual foi o ultimo erro do pipeline de sales?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "sales_orders_pipeline" in payload["answer"]
    assert len(payload["sources"]) == 2


def test_chat_returns_fallback_when_context_is_missing() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"question": "Me fale sobre marketing attribution"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "Ainda não encontrei contexto suficiente" in payload["answer"]
    assert payload["sources"] == []
