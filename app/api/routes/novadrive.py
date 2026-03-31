from fastapi import APIRouter, Query

from app.api.schemas.novadrive import (
    FaturamentoConcessionariaResponse,
    PerformanceVendedorResponse,
)
from app.api.services.novadrive_service import (
    list_faturamento_por_concessionaria,
    list_performance_vendedores,
)

router = APIRouter()


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
