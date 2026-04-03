from fastapi import APIRouter, Query

from app.api.schemas.novadrive import (
    ComparativoFaturamentoNovadriveResponse,
    FaturamentoConcessionariaResponse,
    PrevisaoFaturamentoResponse,
    PerformanceVendedorResponse,
    ResumoFaturamentoNovadriveResponse,
)
from app.api.services.novadrive_service import (
    get_comparativo_faturamento_novadrive,
    get_resumo_faturamento_novadrive,
    list_faturamento_por_concessionaria,
    list_previsao_faturamento,
    list_performance_vendedores,
)

router = APIRouter()


@router.get(
    "/novadrive/faturamento/resumo",
    response_model=ResumoFaturamentoNovadriveResponse,
)
def faturamento_resumo() -> ResumoFaturamentoNovadriveResponse:
    return get_resumo_faturamento_novadrive()


@router.get(
    "/novadrive/faturamento/comparativo",
    response_model=ComparativoFaturamentoNovadriveResponse,
)
def faturamento_comparativo(
    days: int = Query(default=7, ge=1, le=90),
) -> ComparativoFaturamentoNovadriveResponse:
    return get_comparativo_faturamento_novadrive(days)


@router.get(
    "/novadrive/faturamento/concessionarias",
    response_model=FaturamentoConcessionariaResponse,
)
def faturamento_concessionarias(
    limit: int = Query(default=10, ge=1, le=100),
) -> FaturamentoConcessionariaResponse:
    return list_faturamento_por_concessionaria(limit)


@router.get(
    "/novadrive/performance/vendedores",
    response_model=PerformanceVendedorResponse,
)
def performance_vendedores(
    limit: int = Query(default=10, ge=1, le=100),
) -> PerformanceVendedorResponse:
    return list_performance_vendedores(limit)


@router.get(
    "/novadrive/previsoes/faturamento",
    response_model=PrevisaoFaturamentoResponse,
)
def previsao_faturamento(
    limit: int = Query(default=10, ge=1, le=100),
    days_ahead: int = Query(default=7, ge=1, le=30),
) -> PrevisaoFaturamentoResponse:
    return list_previsao_faturamento(limit, days_ahead)
