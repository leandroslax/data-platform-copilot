from fastapi.testclient import TestClient

from app.api.main import app
from app.api.routes import novadrive as novadrive_routes
from app.api.schemas.novadrive import (
    FaturamentoConcessionariaResponse,
    PerformanceVendedorResponse,
    PrevisaoFaturamentoResponse,
    ResumoFaturamentoNovadriveResponse,
)

client = TestClient(app)


def test_faturamento_resumo_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_routes,
        "get_resumo_faturamento_novadrive",
        lambda: ResumoFaturamentoNovadriveResponse(
            faturamento_total=289500123.45,
            total_vendas=2301,
            ticket_medio=125814.92,
            ultima_venda="2026-04-03 00:10:00",
        ),
    )

    response = client.get("/api/v1/novadrive/faturamento/resumo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["faturamento_total"] == 289500123.45
    assert payload["total_vendas"] == 2301


def test_faturamento_concessionarias_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_routes,
        "list_faturamento_por_concessionaria",
        lambda limit: FaturamentoConcessionariaResponse(items=[], total=0, limit=limit),
    )

    response = client.get("/api/v1/novadrive/faturamento/concessionarias")

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert "limit" in payload


def test_performance_vendedores_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_routes,
        "list_performance_vendedores",
        lambda limit: PerformanceVendedorResponse(items=[], total=0, limit=limit),
    )

    response = client.get("/api/v1/novadrive/performance/vendedores")

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert "limit" in payload


def test_previsao_faturamento_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_routes,
        "list_previsao_faturamento",
        lambda limit, days_ahead: PrevisaoFaturamentoResponse(
            items=[],
            total=0,
            limit=limit,
            days_ahead=days_ahead,
        ),
    )

    response = client.get("/api/v1/novadrive/previsoes/faturamento?limit=5&days_ahead=7")

    assert response.status_code == 200
    payload = response.json()
    assert payload["days_ahead"] == 7
    assert payload["limit"] == 5
