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
