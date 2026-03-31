import os

from fastapi.testclient import TestClient

os.environ["DATABRICKS_HOST"] = ""
os.environ["DATABRICKS_TOKEN"] = ""

from app.api.main import app
from app.api.schemas.datasets import DatasetColumn, DatasetDetailResponse
from app.api.schemas.lineage import LineageResponse
from app.api.schemas.novadrive import (
    FaturamentoConcessionariaItem,
    FaturamentoConcessionariaResponse,
    PerformanceVendedorItem,
    PerformanceVendedorResponse,
)
from app.api.services import chat_service

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


def test_chat_answers_explicit_dataset_owner_question(monkeypatch) -> None:
    monkeypatch.setattr(
        chat_service,
        "get_dataset",
        lambda dataset_id: DatasetDetailResponse(
            dataset_id=dataset_id,
            name=dataset_id,
            catalog="samples",
            schema="tpch",
            table="orders",
            type="managed",
            description="Orders table",
            owner="System user",
            columns=[],
            documentation=[],
        ),
    )
    monkeypatch.setattr(
        chat_service,
        "get_lineage",
        lambda dataset_id: LineageResponse(
            dataset_id=dataset_id,
            upstream=[],
            downstream=[],
            related_jobs=[],
        ),
    )

    response = client.post(
        "/api/v1/chat",
        json={"question": "Quem e o owner do dataset samples.tpch.orders?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "samples.tpch.orders" in payload["answer"]
    assert "System user" in payload["answer"]
    assert payload["sources"][0]["id"] == "samples.tpch.orders"


def test_chat_answers_dataset_columns_question(monkeypatch) -> None:
    monkeypatch.setattr(
        chat_service,
        "get_dataset",
        lambda dataset_id: DatasetDetailResponse(
            dataset_id=dataset_id,
            name=dataset_id,
            catalog="samples",
            schema="tpch",
            table="orders",
            type="managed",
            description="Orders table",
            owner="System user",
            columns=[
                DatasetColumn(name="o_orderkey", data_type="bigint", nullable=True, description=None),
                DatasetColumn(name="o_custkey", data_type="bigint", nullable=True, description=None),
            ],
            documentation=[],
        ),
    )
    monkeypatch.setattr(
        chat_service,
        "get_lineage",
        lambda dataset_id: LineageResponse(
            dataset_id=dataset_id,
            upstream=[],
            downstream=[],
            related_jobs=[],
        ),
    )

    response = client.post(
        "/api/v1/chat",
        json={"question": "Quais colunas existem em samples.tpch.orders?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "samples.tpch.orders" in payload["answer"]
    assert "o_orderkey" in payload["answer"]
    assert payload["sources"] == [
        {
            "type": "dataset",
            "id": "samples.tpch.orders",
            "label": "Metadados do dataset",
        }
    ]


def test_chat_answers_novadrive_concessionaria_question(monkeypatch) -> None:
    monkeypatch.setattr(
        chat_service,
        "list_faturamento_por_concessionaria",
        lambda limit: FaturamentoConcessionariaResponse(
            items=[
                FaturamentoConcessionariaItem(
                    id_concessionarias=13,
                    concessionaria="Concessionária NovaDrive Motors Belo Horizonte",
                    cidade="Belo Horizonte",
                    estado="Minas Gerais",
                    sigla_estado="MG",
                    total_vendas=134,
                    faturamento_total=45565767.28,
                    ticket_medio=340043.03,
                )
            ],
            total=1,
            limit=limit,
        ),
    )

    response = client.post(
        "/api/v1/chat",
        json={"question": "Qual concessionaria mais faturou na Novadrive?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "Belo Horizonte" in payload["answer"]
    assert payload["sources"][0]["id"] == "faturamento_por_concessionaria"


def test_chat_answers_novadrive_concessionaria_question_with_accents(monkeypatch) -> None:
    monkeypatch.setattr(
        chat_service,
        "list_faturamento_por_concessionaria",
        lambda limit: FaturamentoConcessionariaResponse(
            items=[
                FaturamentoConcessionariaItem(
                    id_concessionarias=13,
                    concessionaria="Concessionária NovaDrive Motors Belo Horizonte",
                    cidade="Belo Horizonte",
                    estado="Minas Gerais",
                    sigla_estado="MG",
                    total_vendas=134,
                    faturamento_total=45565767.28,
                    ticket_medio=340043.03,
                )
            ],
            total=1,
            limit=limit,
        ),
    )

    response = client.post(
        "/api/v1/chat",
        json={"question": "Quais concessionárias lideram o faturamento da Novadrive?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "Belo Horizonte" in payload["answer"]
    assert payload["sources"][0]["id"] == "faturamento_por_concessionaria"


def test_chat_answers_novadrive_vendedor_question(monkeypatch) -> None:
    monkeypatch.setattr(
        chat_service,
        "list_performance_vendedores",
        lambda limit: PerformanceVendedorResponse(
            items=[
                PerformanceVendedorItem(
                    id_vendedores=40,
                    vendedor_nome="Luciana Freitas",
                    id_concessionarias=19,
                    concessionaria="Concessionária NovaDrive Motors Rio de Janeiro",
                    cidade="Rio de Janeiro",
                    estado="Rio de Janeiro",
                    sigla_estado="RJ",
                    total_vendas=64,
                    faturamento_total=20889360.6,
                    ticket_medio=326396.25,
                )
            ],
            total=1,
            limit=limit,
        ),
    )

    response = client.post(
        "/api/v1/chat",
        json={"question": "Qual vendedor teve maior faturamento na Novadrive?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "Luciana Freitas" in payload["answer"]
    assert payload["sources"][0]["id"] == "performance_vendedores"


def test_chat_returns_fallback_when_context_is_missing() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"question": "Me fale sobre marketing attribution"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert "Ainda não encontrei contexto suficiente" in payload["answer"]
    assert payload["sources"] == []
