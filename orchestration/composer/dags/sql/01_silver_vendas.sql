CREATE OR REPLACE TABLE `data-platform-copilot-dev.silver_novadrive.vendas` AS
WITH vendas_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.vendas_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_vendas
    ORDER BY TIMESTAMP(ingested_at) DESC, COALESCE(data_atualizacao, data_inclusao, data_venda) DESC
  ) = 1
),
clientes_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.clientes_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_clientes
    ORDER BY TIMESTAMP(ingested_at) DESC
  ) = 1
),
veiculos_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.veiculos_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_veiculos
    ORDER BY TIMESTAMP(ingested_at) DESC
  ) = 1
),
vendedores_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.vendedores_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_vendedores
    ORDER BY TIMESTAMP(ingested_at) DESC
  ) = 1
),
concessionarias_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.concessionarias_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_concessionarias
    ORDER BY TIMESTAMP(ingested_at) DESC
  ) = 1
),
cidades_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.cidades_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_cidades
    ORDER BY TIMESTAMP(ingested_at) DESC
  ) = 1
),
estados_dedup AS (
  SELECT *
  FROM `data-platform-copilot-dev.bronze_novadrive.estados_raw`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_estados
    ORDER BY TIMESTAMP(ingested_at) DESC
  ) = 1
)
SELECT
  v.id_vendas,
  v.id_veiculos,
  v.id_concessionarias,
  v.id_vendedores,
  v.id_clientes,
  v.valor_pago,
  v.data_venda,
  v.data_inclusao,
  v.data_atualizacao,
  v.ingested_at,
  cli.cliente,
  cli.endereco,
  vei.nome AS veiculo_nome,
  vei.tipo AS veiculo_tipo,
  vei.valor AS veiculo_valor,
  ven.nome AS vendedor_nome,
  con.concessionaria,
  cid.cidade,
  est.estado,
  est.sigla AS sigla_estado
FROM vendas_dedup v
LEFT JOIN clientes_dedup cli
  ON v.id_clientes = cli.id_clientes
LEFT JOIN veiculos_dedup vei
  ON v.id_veiculos = vei.id_veiculos
LEFT JOIN vendedores_dedup ven
  ON v.id_vendedores = ven.id_vendedores
LEFT JOIN concessionarias_dedup con
  ON v.id_concessionarias = con.id_concessionarias
LEFT JOIN cidades_dedup cid
  ON con.id_cidades = cid.id_cidades
LEFT JOIN estados_dedup est
  ON cid.id_estados = est.id_estados
