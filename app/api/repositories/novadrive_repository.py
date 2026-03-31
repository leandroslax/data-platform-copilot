from typing import Any, Dict, List

from app.api.clients.bigquery_client import BigQueryClient
from app.api.core.config import settings


def list_faturamento_por_concessionaria(limit: int) -> List[Dict[str, Any]]:
    client = BigQueryClient()
    sql = f"""
    SELECT
      id_concessionarias,
      concessionaria,
      cidade,
      estado,
      sigla_estado,
      total_vendas,
      faturamento_total,
      ticket_medio
    FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
    ORDER BY faturamento_total DESC
    LIMIT {limit}
    """
    return client.query(sql)


def list_performance_vendedores(limit: int) -> List[Dict[str, Any]]:
    client = BigQueryClient()
    sql = f"""
    SELECT
      id_vendedores,
      vendedor_nome,
      id_concessionarias,
      concessionaria,
      cidade,
      estado,
      sigla_estado,
      total_vendas,
      faturamento_total,
      ticket_medio
    FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.performance_vendedores`
    ORDER BY faturamento_total DESC
    LIMIT {limit}
    """
    return client.query(sql)
