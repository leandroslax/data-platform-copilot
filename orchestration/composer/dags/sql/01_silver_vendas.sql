CREATE OR REPLACE TABLE `data-platform-copilot-dev.silver_novadrive.vendas` AS
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
FROM `data-platform-copilot-dev.bronze_novadrive.vendas_raw` v
LEFT JOIN `data-platform-copilot-dev.bronze_novadrive.clientes_raw` cli
  ON v.id_clientes = cli.id_clientes
LEFT JOIN `data-platform-copilot-dev.bronze_novadrive.veiculos_raw` vei
  ON v.id_veiculos = vei.id_veiculos
LEFT JOIN `data-platform-copilot-dev.bronze_novadrive.vendedores_raw` ven
  ON v.id_vendedores = ven.id_vendedores
LEFT JOIN `data-platform-copilot-dev.bronze_novadrive.concessionarias_raw` con
  ON v.id_concessionarias = con.id_concessionarias
LEFT JOIN `data-platform-copilot-dev.bronze_novadrive.cidades_raw` cid
  ON con.id_cidades = cid.id_cidades
LEFT JOIN `data-platform-copilot-dev.bronze_novadrive.estados_raw` est
  ON cid.id_estados = est.id_estados
