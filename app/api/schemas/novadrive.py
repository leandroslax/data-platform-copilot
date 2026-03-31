from typing import List, Optional

from pydantic import BaseModel


class FaturamentoConcessionariaItem(BaseModel):
    id_concessionarias: int
    concessionaria: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    sigla_estado: Optional[str] = None
    total_vendas: int
    faturamento_total: float
    ticket_medio: float


class FaturamentoConcessionariaResponse(BaseModel):
    items: List[FaturamentoConcessionariaItem]
    total: int
    limit: int


class PerformanceVendedorItem(BaseModel):
    id_vendedores: int
    vendedor_nome: str
    id_concessionarias: int
    concessionaria: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    sigla_estado: Optional[str] = None
    total_vendas: int
    faturamento_total: float
    ticket_medio: float


class PerformanceVendedorResponse(BaseModel):
    items: List[PerformanceVendedorItem]
    total: int
    limit: int
