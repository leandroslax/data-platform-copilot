from app.api.repositories.novadrive_repository import (
    get_comparativo_faturamento_novadrive as get_comparativo_faturamento_record,
    get_resumo_faturamento_novadrive as get_resumo_faturamento_record,
    list_faturamento_por_concessionaria as list_faturamento_records,
    list_previsao_faturamento as list_previsao_records,
    list_performance_vendedores as list_performance_records,
)
from app.api.schemas.novadrive import (
    ComparativoFaturamentoNovadriveResponse,
    FaturamentoConcessionariaItem,
    FaturamentoConcessionariaResponse,
    PrevisaoFaturamentoItem,
    PrevisaoFaturamentoResponse,
    PerformanceVendedorItem,
    PerformanceVendedorResponse,
    ResumoFaturamentoNovadriveResponse,
)


def get_comparativo_faturamento_novadrive(days: int) -> ComparativoFaturamentoNovadriveResponse:
    record = get_comparativo_faturamento_record(days)

    return ComparativoFaturamentoNovadriveResponse(
        dias=int(record.get("dias") or days),
        periodo_atual_inicio=record.get("periodo_atual_inicio") or "",
        periodo_atual_fim=record.get("periodo_atual_fim") or "",
        periodo_anterior_inicio=record.get("periodo_anterior_inicio") or "",
        periodo_anterior_fim=record.get("periodo_anterior_fim") or "",
        faturamento_periodo_atual=float(record.get("faturamento_periodo_atual") or 0.0),
        faturamento_periodo_anterior=float(record.get("faturamento_periodo_anterior") or 0.0),
        vendas_periodo_atual=int(record.get("vendas_periodo_atual") or 0),
        vendas_periodo_anterior=int(record.get("vendas_periodo_anterior") or 0),
        variacao_percentual=float(record.get("variacao_percentual") or 0.0),
    )


def get_resumo_faturamento_novadrive() -> ResumoFaturamentoNovadriveResponse:
    record = get_resumo_faturamento_record()

    return ResumoFaturamentoNovadriveResponse(
        faturamento_total=float(record.get("faturamento_total") or 0.0),
        total_vendas=int(record.get("total_vendas") or 0),
        ticket_medio=float(record.get("ticket_medio") or 0.0),
        ultima_venda=record.get("ultima_venda"),
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


def list_previsao_faturamento(limit: int, days_ahead: int) -> PrevisaoFaturamentoResponse:
    records = list_previsao_records(limit, days_ahead)

    items = [
        PrevisaoFaturamentoItem(
            data_previsao=record["data_previsao"],
            id_concessionarias=record["id_concessionarias"],
            concessionaria=record["concessionaria"],
            cidade=record.get("cidade"),
            estado=record.get("estado"),
            sigla_estado=record.get("sigla_estado"),
            faturamento_previsto=float(record["faturamento_previsto"]),
            limite_inferior=float(record["limite_inferior"]),
            limite_superior=float(record["limite_superior"]),
            confidence_level=float(record["confidence_level"]),
        )
        for record in records
    ]

    return PrevisaoFaturamentoResponse(
        items=items,
        total=len(items),
        limit=limit,
        days_ahead=days_ahead,
    )
