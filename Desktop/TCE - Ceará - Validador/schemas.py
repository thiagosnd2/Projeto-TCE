# -*- coding: utf-8 -*-
"""
Especificação de campos (layout) das Tabelas 501 a 513 do
Manual do SIM 2026 (TCE-CE), referentes ao bloco:

  5.3.27  Processos Administrativos para Contratações: 501
  5.3.28  Publicações de Processos Administrativos para Contratações: 502
  5.3.29  Tipos de Responsáveis pela Contratação: 503
  5.3.30  Identificação dos Responsáveis pela Contratação: 504
  5.3.31  Licitantes e Fornecedores de Bens e Serviços: 505
  5.3.32  Itens que Compõem os Bens ou Serviços: 506
  5.3.33  Dotações Utilizadas para Contratações: 507
  5.3.34  Contratos: 511
  5.3.35  Contratados: 513

Cada campo é descrito por um FieldSpec. As regras de negócio adicionais
(campos condicionais, herança entre tabelas, etc.) NÃO estão aqui —
elas estão implementadas em regras.py, pois dependem de mais de um
campo/tabela.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class FieldSpec:
    idx: int                       # número do campo (1-based), conforme Manual
    name: str                      # nome do campo
    kind: str                      # 'C' (caractere) ou 'N' (numérico)
    size: int                      # tamanho máximo (ou exato) em posições (parte inteira, se decimal)
    exact: bool = True             # True = tamanho EXATO; False = "ATÉ x posições" (variável)
    decimals: Optional[int] = None # nº de casas decimais (só para campos numéricos com decimais)
    required: bool = True          # False = campo pode ficar vazio/zero conforme regra de negócio
    allowed: Optional[List[str]] = None  # lista de códigos válidos (match exato)
    overwritable: bool = False     # campo marcado com (*) no Manual (atualizável via requerimento)
    note: str = ""                 # observação livre


# ---------------------------------------------------------------------------
# 501 — PROCESSOS ADMINISTRATIVOS PARA CONTRATAÇÕES  (arquivo LI*.LCO)
# ---------------------------------------------------------------------------
T501 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["501"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "Data de Autuação do Processo", "N", 8),
    FieldSpec(4, "Número do Processo Administrativo", "C", 15, exact=False),
    FieldSpec(5, "Espécie do Processo Administrativo", "C", 1,
              allowed=["N", "F", "D", "I", "R", "P", "C", "Q", "M"], overwritable=True),
    FieldSpec(6, "Descrição do Objeto", "C", 510, exact=False, overwritable=True),
    FieldSpec(7, "Valor Total do Orçamento Estimado", "N", 10, decimals=2, overwritable=True),
    FieldSpec(8, "CPF do Responsável pelo Parecer Jurídico", "C", 11, overwritable=True),
    FieldSpec(9, "Nome do Responsável pelo Parecer Jurídico", "C", 40, exact=False, overwritable=True),
    FieldSpec(10, "CPF do Gestor da UG do Responsável pela Contratação", "C", 11),
    FieldSpec(11, "Data da Portaria de criação/designação (herdado 503)", "N", 8),
    FieldSpec(12, "Nº Sequencial de comissão/equipe/agente (herdado 503)", "C", 2),
    FieldSpec(13, "CPF do Responsável pela Homologação/Ratificação", "C", 11, overwritable=True),
    FieldSpec(14, "Nome do Responsável pela Homologação/Ratificação", "C", 40, exact=False, overwritable=True),
    FieldSpec(15, "Data de Homologação ou Ratificação", "N", 8),
    FieldSpec(16, "Hora da Realização da Licitação", "C", 5, required=False,
              note="Preencher com \"\" quando NÃO for processo licitatório (e.7)"),
    FieldSpec(17, "Data da Realização da Licitação", "N", 8, required=False,
              note="Preencher com 0 quando NÃO for processo licitatório (e.7)"),
    FieldSpec(18, "Modalidade da Licitação", "C", 1,
              allowed=["1", "2", "3", "4", "5", "6", "7", "8", "9"], overwritable=True),
    FieldSpec(19, "Critério de Julgamento da Licitação", "C", 1,
              allowed=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], overwritable=True),
    FieldSpec(20, "Valor Limite Superior Desclassificatório", "N", 10, decimals=2,
              required=False, overwritable=True),
    FieldSpec(21, "Justificativa do Preço Estabelecido", "C", 510, exact=False, required=False,
              overwritable=True, note="Só p/ Dispensa/Inexigib./Adesão (e.8); senão \"\""),
    FieldSpec(22, "Motivo da escolha do Fornecedor", "C", 510, exact=False, required=False, overwritable=True),
    FieldSpec(23, "Fundamentação Legal", "C", 255, exact=False, required=False, overwritable=True),
    FieldSpec(24, "Órgão Gerenciador da Ata de Registro de Preço", "C", 255, exact=False, required=False,
              overwritable=True),
    FieldSpec(25, "Data de Referência da Documentação", "N", 6),
    FieldSpec(26, "CPF do Responsável pela Cotação de Preços", "C", 11, overwritable=True),
    FieldSpec(27, "Nome do Responsável pela Cotação de Preços", "C", 40, exact=False, overwritable=True),
    FieldSpec(28, "CPF do Responsável pelo Termo de Referência/Projeto Básico", "C", 11, overwritable=True),
    FieldSpec(29, "Nome do Responsável pelo Termo de Referência/Projeto Básico", "C", 40, exact=False,
              overwritable=True),
    FieldSpec(30, "Forma da Contratação", "C", 1, allowed=["E", "P"]),
    FieldSpec(31, "Tipo de Disputa", "C", 1, allowed=["A", "F", "C"], required=False,
              note="\"\" quando NÃO for processo licitatório (e.7)"),
    FieldSpec(32, "URL da plataforma de realização", "C", 50, exact=False, required=False,
              note="\"\" em procedimentos presenciais/não aplicável (e.7)"),
    FieldSpec(33, "Sistema de Registro de Preços", "C", 1, allowed=["S", "N"]),
    FieldSpec(34, "Número do Id Contratação PNCP", "C", 25, required=False,
              note="\"\" se não cadastrado no PNCP"),
    FieldSpec(35, "Número do Id Ata PNCP", "C", 31, required=False,
              note="\"\" se não cadastrada no PNCP"),
]

# ---------------------------------------------------------------------------
# 502 — PUBLICAÇÕES DE PROCESSOS ADMINISTRATIVOS PARA CONTRATAÇÕES (PE*.LCO)
# ---------------------------------------------------------------------------
T502 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["502"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "Data de Autuação do Processo (herdado 501)", "N", 8),
    FieldSpec(4, "Número do Processo (herdado 501)", "C", 15, exact=False),
    FieldSpec(5, "Nº Sequencial da Publicação", "C", 2),
    FieldSpec(6, "Código do Veículo de Publicação", "C", 1,
              allowed=["1", "2", "3", "4", "5", "9"], overwritable=True),
    FieldSpec(7, "Descrição do Veículo de Publicação", "C", 255, exact=False, overwritable=True),
    FieldSpec(8, "Data da Publicação", "N", 8, overwritable=True),
    FieldSpec(9, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
# 503 — TIPOS DE RESPONSÁVEIS PELA CONTRATAÇÃO (CL*.LCO)
# ---------------------------------------------------------------------------
T503 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["503"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "CPF do Gestor da Unidade Gestora", "C", 11),
    FieldSpec(4, "Data da Portaria de criação/designação", "N", 8),
    FieldSpec(5, "Nº Sequencial de comissão/equipe/agente na UG", "C", 2),
    FieldSpec(6, "Número da Portaria de criação/designação", "C", 15, exact=False, overwritable=True),
    FieldSpec(7, "Tipo do Responsável de Contratação", "C", 1,
              allowed=["1", "2", "3", "4"], overwritable=True),
    FieldSpec(8, "Data de Extinção de comissão/equipe/agente", "N", 8, required=False,
              overwritable=True, note="0 inicialmente"),
    FieldSpec(9, "Número da Portaria de Extinção", "C", 15, exact=False, required=False,
              overwritable=True, note="\"\" inicialmente"),
    FieldSpec(10, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
# 504 — IDENTIFICAÇÃO DOS RESPONSÁVEIS PELA CONTRATAÇÃO (MC*.LCO)
# ---------------------------------------------------------------------------
T504 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["504"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "CPF do Gestor da UG (herdado 503)", "C", 11),
    FieldSpec(4, "Data da Portaria de criação/designação (herdado 503)", "N", 8),
    FieldSpec(5, "Nº Sequencial de comissão/equipe/agente (herdado 503)", "C", 2),
    FieldSpec(6, "CPF do Responsável pela Contratação", "C", 11),
    FieldSpec(7, "Nome do Responsável pela Contratação", "C", 60, exact=False, overwritable=True),
    FieldSpec(8, "Endereço Completo do Responsável", "C", 255, exact=False, required=False,
              overwritable=True),
    FieldSpec(9, "Número do Telefone do Responsável", "C", 11, exact=False, required=False,
              overwritable=True),
    FieldSpec(10, "Função do Responsável pela Contratação", "C", 1,
              allowed=["1", "2", "3", "4", "5", "6"], overwritable=True),
    FieldSpec(11, "Data de Nomeação do Responsável", "N", 8, overwritable=True),
    FieldSpec(12, "Data de Exoneração do Responsável", "N", 8, required=False,
              overwritable=True, note="0 inicialmente"),
    FieldSpec(13, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
# 505 — LICITANTES E FORNECEDORES DE BENS E SERVIÇOS (LT*.LCO)
# ---------------------------------------------------------------------------
T505 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["505"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "Data de Autuação do Processo (herdado 501)", "N", 8),
    FieldSpec(4, "Número do Processo (herdado 501)", "C", 15, exact=False),
    FieldSpec(5, "Tipo de Documento de Identificação", "C", 1, allowed=["1", "2"]),
    FieldSpec(6, "Número do Documento de Identificação", "C", 25, exact=False),
    FieldSpec(7, "Nome ou Razão Social", "C", 60, exact=False, overwritable=True),
    FieldSpec(8, "Endereço Completo", "C", 255, exact=False, required=False, overwritable=True),
    FieldSpec(9, "Número do Telefone", "C", 11, exact=False, required=False, overwritable=True),
    FieldSpec(10, "Número do CEP", "C", 8, required=False, overwritable=True),
    FieldSpec(11, "Nome do Município", "C", 30, exact=False, required=False, overwritable=True),
    FieldSpec(12, "Unidade da Federação", "C", 2, required=False, overwritable=True),
    FieldSpec(13, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
# 506 — ITENS QUE COMPÕEM OS BENS OU SERVIÇOS (TL*.LCO)
# ---------------------------------------------------------------------------
T506 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["506"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "Data de Autuação do Processo (herdado 501)", "N", 8),
    FieldSpec(4, "Número do Processo (herdado 501)", "C", 15, exact=False),
    FieldSpec(5, "Nº Sequencial do Item", "N", 4, exact=False),
    FieldSpec(6, "Descrição do Item", "C", 255, exact=False, overwritable=True),
    FieldSpec(7, "Unidade do Item", "C", 10, exact=False, overwritable=True),
    FieldSpec(8, "Quantidade do Item", "N", 10, decimals=2, overwritable=True),
    FieldSpec(9, "Valor Unitário do Item", "N", 10, decimals=6, overwritable=True),
    FieldSpec(10, "Valor Proposto pelo Licitante Vencedor/Fornecedor", "N", 10, decimals=4,
              overwritable=True),
    FieldSpec(11, "Tipo de Documento de Identificação (herdado 505)", "C", 1,
              allowed=["1", "2"], overwritable=True),
    FieldSpec(12, "Número do Documento de Identificação (herdado 505)", "C", 25, exact=False,
              overwritable=True),
    FieldSpec(13, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
# 507 — DOTAÇÕES UTILIZADAS PARA CONTRATAÇÕES (DL*.LCO)
# ---------------------------------------------------------------------------
T507 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["507"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "Data de Autuação do Processo (herdado 501)", "N", 8),
    FieldSpec(4, "Número do Processo (herdado 501)", "C", 15, exact=False),
    FieldSpec(5, "Exercício do Orçamento", "N", 6),
    FieldSpec(6, "Código do Órgão", "C", 2),
    FieldSpec(7, "Código da Unidade Orçamentária", "C", 2),
    FieldSpec(8, "Código da Função", "C", 2),
    FieldSpec(9, "Código da Subfunção", "C", 3),
    FieldSpec(10, "Código do Programa", "C", 4),
    FieldSpec(11, "Código de Projeto ou Atividade", "C", 1,
              allowed=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]),
    FieldSpec(12, "Número do Projeto ou Atividade", "C", 3),
    FieldSpec(13, "Número do Sub-projeto ou Sub-atividade", "C", 4),
    FieldSpec(14, "Código do Elemento de Despesa", "C", 8),
    FieldSpec(15, "Código do Grupo da Fonte", "C", 1, allowed=["1", "2", "9"]),
    FieldSpec(16, "Código da Especificação da Fonte", "C", 9),
    FieldSpec(17, "Valor Utilizado na Contratação", "N", 10, decimals=2, overwritable=True),
    FieldSpec(18, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
# 511 — CONTRATOS (CO*.LCO)
# ---------------------------------------------------------------------------
T511 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["511"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "CPF do Gestor Responsável pela Celebração", "C", 11),
    FieldSpec(4, "Número do Contrato", "C", 15, exact=False),
    FieldSpec(5, "Data de Celebração do Contrato", "N", 8),
    FieldSpec(6, "Tipo de Objeto Contratado", "C", 1, allowed=list("ABCDEFGHIJKLMNOPQR")),
    FieldSpec(7, "Modalidade do Contrato", "C", 2,
              allowed=["OR", "AA", "AR", "AP", "PA", "PR", "RE"], overwritable=True),
    FieldSpec(8, "CPF do Gestor do Contrato Original", "C", 11, required=False,
              note="\"\" se contrato Original (e.3)"),
    FieldSpec(9, "Número do Contrato Original", "C", 15, exact=False, required=False, overwritable=True,
              note="\"\" se contrato Original (e.3)"),
    FieldSpec(10, "Data que o Contrato Original foi celebrado", "N", 8, required=False, overwritable=True,
              note="0 se contrato Original (e.3)"),
    FieldSpec(11, "Data de Início da Vigência do Contrato", "N", 8, overwritable=True),
    FieldSpec(12, "Data Prevista para o Fim da Vigência", "N", 8, overwritable=True),
    FieldSpec(13, "Descrição do Objeto do Contrato", "C", 255, exact=False, overwritable=True),
    FieldSpec(14, "Valor Total do Contrato", "N", 10, decimals=2,
              note="Aditivo de prazo puro = 0.00 (e.6); aditivos de valor sempre positivos (e.4)"),
    FieldSpec(15, "Data de Início da Obra/Serviço de Engenharia", "N", 8, required=False,
              note="0 se não for obra/serviço de engenharia"),
    FieldSpec(16, "Tipo (Obra ou Serviço de Engenharia)", "C", 1, allowed=["O", "S"], required=False,
              note="\"\" se não for obra/serviço de engenharia"),
    FieldSpec(17, "Número da Obra ou Serviço de Engenharia", "C", 4, required=False,
              note="\"\" se não for obra/serviço de engenharia"),
    FieldSpec(18, "Data Prevista para o Término da Obra", "N", 8, required=False,
              note="0 se não for obra/serviço de engenharia"),
    FieldSpec(19, "Data de Referência da Documentação", "N", 6),
    FieldSpec(20, "Data de Autuação do Processo Administrativo", "N", 8, required=False,
              note="0 se não oriundo de Processo (e.8)"),
    FieldSpec(21, "Número do Processo Administrativo", "C", 15, exact=False, required=False,
              note="\"\" se não oriundo de Processo (e.8)"),
    FieldSpec(22, "CPF do Fiscal do Contrato", "C", 11, overwritable=True),
    FieldSpec(23, "Nome do Fiscal do Contrato", "C", 40, exact=False, overwritable=True),
    FieldSpec(24, "Número do Id Contrato PNCP", "C", 25, required=False,
              note="\"\" se não cadastrado no PNCP"),
]

# ---------------------------------------------------------------------------
# 513 — CONTRATADOS (CT*.LCO)
# ---------------------------------------------------------------------------
T513 = [
    FieldSpec(1, "Tipo do Documento", "C", 3, allowed=["513"]),
    FieldSpec(2, "Código do Município", "C", 3),
    FieldSpec(3, "CPF do Gestor Responsável (herdado 511)", "C", 11),
    FieldSpec(4, "Número do Contrato (herdado 511)", "C", 15, exact=False),
    FieldSpec(5, "Data que o Contrato foi firmado (herdado 511)", "N", 8),
    FieldSpec(6, "Tipo de Documento de Identificação do Contratado", "C", 1, allowed=["1", "2"]),
    FieldSpec(7, "Número do Documento de Identificação", "C", 25, exact=False),
    FieldSpec(8, "Nome ou Razão Social do Contratado", "C", 60, exact=False, overwritable=True),
    FieldSpec(9, "Endereço Completo do Contratado", "C", 255, exact=False, required=False,
              overwritable=True),
    FieldSpec(10, "Número do Telefone do Contratado", "C", 11, exact=False, required=False,
              overwritable=True),
    FieldSpec(11, "Número do CEP do Contratado", "C", 8, required=False, overwritable=True),
    FieldSpec(12, "Nome do Município do Contratado", "C", 30, exact=False, required=False,
              overwritable=True),
    FieldSpec(13, "Unidade da Federação do Contratado", "C", 2, required=False, overwritable=True),
    FieldSpec(14, "Data de Referência da Documentação", "N", 6),
]

# ---------------------------------------------------------------------------
TABLE_SCHEMAS = {
    "501": T501,
    "502": T502,
    "503": T503,
    "504": T504,
    "505": T505,
    "506": T506,
    "507": T507,
    "511": T511,
    "513": T513,
}

# Prefixo do nome do arquivo (2 letras) -> tipo de documento, conforme item 5.2 do Manual
FILE_PREFIX_TO_TABLE = {
    "LI": "501",
    "PE": "502",
    "CL": "503",
    "MC": "504",
    "LT": "505",
    "TL": "506",
    "DL": "507",
    "CO": "511",
    "CT": "513",
}
