from app.api.services import novadrive_service


def test_list_faturamento_por_concessionaria(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_service,
        "list_faturamento_records",
        lambda limit: [
            {
                "id_concessionarias": 13,
                "concessionaria": "Concessionária NovaDrive Motors Belo Horizonte",
                "cidade": "Belo Horizonte",
                "estado": "Minas Gerais",
                "sigla_estado": "MG",
                "total_vendas": 134,
                "faturamento_total": 45565767.28,
                "ticket_medio": 340043.03,
            }
        ],
    )

    response = novadrive_service.list_faturamento_por_concessionaria(10)

    assert response.total == 1
    assert response.items[0].concessionaria == "Concessionária NovaDrive Motors Belo Horizonte"


def test_get_resumo_faturamento_novadrive(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_service,
        "get_resumo_faturamento_record",
        lambda: {
            "faturamento_total": 289500123.45,
            "total_vendas": 2301,
            "ticket_medio": 125814.92,
            "ultima_venda": "2026-04-03 00:10:00",
        },
    )

    response = novadrive_service.get_resumo_faturamento_novadrive()

    assert response.faturamento_total == 289500123.45
    assert response.total_vendas == 2301
    assert response.ticket_medio == 125814.92


def test_get_comparativo_faturamento_novadrive(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_service,
        "get_comparativo_faturamento_record",
        lambda days: {
            "dias": days,
            "periodo_atual_inicio": "2026-03-27",
            "periodo_atual_fim": "2026-04-02",
            "periodo_anterior_inicio": "2026-03-20",
            "periodo_anterior_fim": "2026-03-26",
            "faturamento_periodo_atual": 12000000.0,
            "faturamento_periodo_anterior": 10000000.0,
            "vendas_periodo_atual": 42,
            "vendas_periodo_anterior": 37,
            "variacao_percentual": 20.0,
        },
    )

    response = novadrive_service.get_comparativo_faturamento_novadrive(7)

    assert response.dias == 7
    assert response.faturamento_periodo_atual == 12000000.0
    assert response.variacao_percentual == 20.0


def test_list_performance_vendedores(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_service,
        "list_performance_records",
        lambda limit: [
            {
                "id_vendedores": 40,
                "vendedor_nome": "Luciana Freitas",
                "id_concessionarias": 19,
                "concessionaria": "Concessionária NovaDrive Motors Rio de Janeiro",
                "cidade": "Rio de Janeiro",
                "estado": "Rio de Janeiro",
                "sigla_estado": "RJ",
                "total_vendas": 64,
                "faturamento_total": 20889360.6,
                "ticket_medio": 326396.25,
            }
        ],
    )

    response = novadrive_service.list_performance_vendedores(10)

    assert response.total == 1
    assert response.items[0].vendedor_nome == "Luciana Freitas"


def test_list_previsao_faturamento(monkeypatch) -> None:
    monkeypatch.setattr(
        novadrive_service,
        "list_previsao_records",
        lambda limit, days_ahead: [
            {
                "data_previsao": "2026-04-10",
                "id_concessionarias": 13,
                "concessionaria": "Concessionária NovaDrive Motors Belo Horizonte",
                "cidade": "Belo Horizonte",
                "estado": "Minas Gerais",
                "sigla_estado": "MG",
                "faturamento_previsto": 48500000.0,
                "limite_inferior": 43000000.0,
                "limite_superior": 52000000.0,
                "confidence_level": 0.8,
            }
        ],
    )

    response = novadrive_service.list_previsao_faturamento(10, 7)

    assert response.total == 1
    assert response.days_ahead == 7
    assert response.items[0].data_previsao == "2026-04-10"
