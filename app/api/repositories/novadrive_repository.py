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


def get_comparativo_faturamento_novadrive(days: int) -> Dict[str, Any]:
    client = BigQueryClient()
    sql = f"""
    WITH bounds AS (
      SELECT
        CURRENT_DATE("America/Sao_Paulo") AS hoje,
        DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL {days} DAY) AS atual_inicio,
        DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL 1 DAY) AS atual_fim,
        DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL {days * 2} DAY) AS anterior_inicio,
        DATE_SUB(CURRENT_DATE("America/Sao_Paulo"), INTERVAL {days + 1} DAY) AS anterior_fim
    ),
    base AS (
      SELECT
        DATE(data_venda, "America/Sao_Paulo") AS dia_venda,
        valor_pago
      FROM `{settings.bigquery_project_id}.{settings.novadrive_silver_dataset}.vendas`
    )
    SELECT
      {days} AS dias,
      FORMAT_DATE('%Y-%m-%d', atual_inicio) AS periodo_atual_inicio,
      FORMAT_DATE('%Y-%m-%d', atual_fim) AS periodo_atual_fim,
      FORMAT_DATE('%Y-%m-%d', anterior_inicio) AS periodo_anterior_inicio,
      FORMAT_DATE('%Y-%m-%d', anterior_fim) AS periodo_anterior_fim,
      SUM(CASE WHEN dia_venda BETWEEN atual_inicio AND atual_fim THEN valor_pago ELSE 0 END) AS faturamento_periodo_atual,
      SUM(CASE WHEN dia_venda BETWEEN anterior_inicio AND anterior_fim THEN valor_pago ELSE 0 END) AS faturamento_periodo_anterior,
      COUNTIF(dia_venda BETWEEN atual_inicio AND atual_fim) AS vendas_periodo_atual,
      COUNTIF(dia_venda BETWEEN anterior_inicio AND anterior_fim) AS vendas_periodo_anterior,
      SAFE_MULTIPLY(
        SAFE_DIVIDE(
          SUM(CASE WHEN dia_venda BETWEEN atual_inicio AND atual_fim THEN valor_pago ELSE 0 END)
          - SUM(CASE WHEN dia_venda BETWEEN anterior_inicio AND anterior_fim THEN valor_pago ELSE 0 END),
          NULLIF(SUM(CASE WHEN dia_venda BETWEEN anterior_inicio AND anterior_fim THEN valor_pago ELSE 0 END), 0)
        ),
        100
      ) AS variacao_percentual
    FROM base
    CROSS JOIN bounds
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
