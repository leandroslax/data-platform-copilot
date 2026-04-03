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


class ResumoFaturamentoNovadriveResponse(BaseModel):
    faturamento_total: float
    total_vendas: int
    ticket_medio: float
    ultima_venda: Optional[str] = None


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


class PrevisaoFaturamentoItem(BaseModel):
    data_previsao: str
    id_concessionarias: int
    concessionaria: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    sigla_estado: Optional[str] = None
    faturamento_previsto: float
    limite_inferior: float
    limite_superior: float
    confidence_level: float


class PrevisaoFaturamentoResponse(BaseModel):
    items: List[PrevisaoFaturamentoItem]
    total: int
    limit: int
    days_ahead: int
