from app.api.repositories.novadrive_repository import (
    list_faturamento_por_concessionaria as list_faturamento_records,
    list_performance_vendedores as list_performance_records,
)
from app.api.schemas.novadrive import (
    FaturamentoConcessionariaItem,
    FaturamentoConcessionariaResponse,
    PerformanceVendedorItem,
    PerformanceVendedorResponse,
)


def list_faturamento_por_concessionaria(limit: int) -> FaturamentoConcessionariaResponse:
    records = list_faturamento_records(limit)

    items = [
        FaturamentoConcessionariaItem(
            id_concessionarias=record["id_concessionarias"],
            concessionaria=record["concessionaria"],
            cidade=record.get("cidade"),
            estado=record.get("estado"),
            sigla_estado=record.get("sigla_estado"),
            total_vendas=record["total_vendas"],
            faturamento_total=float(record["faturamento_total"]),
            ticket_medio=float(record["ticket_medio"]),
        )
        for record in records
    ]

    return FaturamentoConcessionariaResponse(
        items=items,
        total=len(items),
        limit=limit,
    )


def list_performance_vendedores(limit: int) -> PerformanceVendedorResponse:
    records = list_performance_records(limit)

    items = [
        PerformanceVendedorItem(
            id_vendedores=record["id_vendedores"],
            vendedor_nome=record["vendedor_nome"],
            id_concessionarias=record["id_concessionarias"],
            concessionaria=record["concessionaria"],
            cidade=record.get("cidade"),
            estado=record.get("estado"),
            sigla_estado=record.get("sigla_estado"),
            total_vendas=record["total_vendas"],
            faturamento_total=float(record["faturamento_total"]),
            ticket_medio=float(record["ticket_medio"]),
        )
        for record in records
    ]

    return PerformanceVendedorResponse(
        items=items,
        total=len(items),
        limit=limit,
    )
