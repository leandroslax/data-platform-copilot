from typing import Any, Dict, List

from app.api.clients.bigquery_client import BigQueryClient
from app.api.core.config import settings


def get_resumo_faturamento_novadrive() -> Dict[str, Any]:
    client = BigQueryClient()
    sql = f"""
    SELECT
      SUM(faturamento_total) AS faturamento_total,
      SUM(total_vendas) AS total_vendas,
      SAFE_DIVIDE(SUM(faturamento_total), SUM(total_vendas)) AS ticket_medio,
      FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', MAX(ultima_venda), 'America/Sao_Paulo') AS ultima_venda
    FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
    """
    results = client.query(sql)
    return results[0] if results else {}


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


def list_previsao_faturamento(limit: int, days_ahead: int) -> List[Dict[str, Any]]:
    client = BigQueryClient()
    sql = f"""
    SELECT
      FORMAT_DATE('%Y-%m-%d', data_previsao) AS data_previsao,
      id_concessionarias,
      concessionaria,
      cidade,
      estado,
      sigla_estado,
      faturamento_previsto,
      limite_inferior,
      limite_superior,
      confidence_level
    FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.previsao_faturamento_concessionarias`
    WHERE data_previsao BETWEEN CURRENT_DATE("America/Sao_Paulo")
      AND DATE_ADD(CURRENT_DATE("America/Sao_Paulo"), INTERVAL {days_ahead} DAY)
    ORDER BY data_previsao, faturamento_previsto DESC
    LIMIT {limit}
    """
    return client.query(sql)
