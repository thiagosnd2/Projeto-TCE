#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador SIM — Bloco de Contratações (Tabelas 501 a 513)
Manual do SIM 2026 — TCE-CE (itens 5.3.27 a 5.3.35)

Valida arquivos-texto do SIM referentes a:
  501 - Processos Administrativos para Contratações   (LI*.LCO)
  502 - Publicações de Processos Adm. p/ Contratações  (PE*.LCO)
  503 - Tipos de Responsáveis pela Contratação         (CL*.LCO)
  504 - Identificação dos Responsáveis pela Contratação(MC*.LCO)
  505 - Licitantes e Fornecedores de Bens e Serviços   (LT*.LCO)
  506 - Itens que Compõem os Bens ou Serviços          (TL*.LCO)
  507 - Dotações Utilizadas para Contratações          (DL*.LCO)
  511 - Contratos                                      (CO*.LCO)
  513 - Contratados                                    (CT*.LCO)

USO:
    python validador_sim.py --dir /caminho/da/pasta [--saida relatorio.txt]

    A pasta deve conter os arquivos .LCO (ou .lco) gerados para o mês de
    referência. O validador identifica cada arquivo pelo prefixo de 2
    letras do nome (ex.: LI202601.LCO -> tabela 501) e também confere o
    campo 1 ("Tipo do Documento") de cada linha.

    Também é possível apontar arquivos individuais:
    python validador_sim.py --arquivos LI202601.LCO CO202601.LCO ...

SAÍDA:
    Relatório com:
      1) Erros de LAYOUT (tipo/tamanho/domínio/obrigatoriedade) por campo,
         linha a linha;
      2) Erros de REGRAS DE NEGÓCIO e INTEGRIDADE REFERENCIAL entre as
         tabelas (ex.: processo citado em 502/505/506/507 mas ausente
         em 501; aditivo de contrato sem contrato original; etc.).
"""

import argparse
import os
import sys
from collections import defaultdict

from schemas import TABLE_SCHEMAS, FILE_PREFIX_TO_TABLE
from parser import read_sim_file, validar_campos_registro, ParsedRecord
from regras import rodar_todas_regras


def identificar_tabela(caminho_arquivo: str) -> str:
    nome = os.path.basename(caminho_arquivo)
    prefixo = nome[:2].upper()
    return FILE_PREFIX_TO_TABLE.get(prefixo, "")


def coletar_arquivos(diretorio: str) -> list:
    arquivos = []
    for nome in sorted(os.listdir(diretorio)):
        if nome.upper().endswith(".LCO"):
            arquivos.append(os.path.join(diretorio, nome))
    return arquivos


def validar_arquivo(caminho: str, tabela: str, dados_por_tabela: dict,
                     erros_layout: list):
    registros = read_sim_file(caminho)
    schema = TABLE_SCHEMAS[tabela]
    nome_arq = os.path.basename(caminho)

    for rec in registros:
        # confere se o campo 1 (Tipo do Documento) bate com a tabela do arquivo
        tipo_doc_linha = rec.raw[0].strip() if rec.raw else ""
        if tipo_doc_linha != tabela:
            erros_layout.append(
                f"[{nome_arq}] linha {rec.linha}: campo 1 (Tipo do Documento) = "
                f"'{tipo_doc_linha}', esperado '{tabela}' para este arquivo.")
            continue
        erros_campo = validar_campos_registro(schema, rec.raw, rec.linha)
        for e in erros_campo:
            erros_layout.append(
                f"[{nome_arq}] linha {e.linha}, campo {e.campo_idx} "
                f"({e.campo_nome}) = '{e.valor}': {e.mensagem}")
        dados_por_tabela[tabela].append(rec)


def main():
    ap = argparse.ArgumentParser(
        description="Validador SIM — Bloco de Contratações (501-513), "
                    "Manual do SIM 2026, TCE-CE.")
    ap.add_argument("--dir", help="Diretório contendo os arquivos .LCO")
    ap.add_argument("--arquivos", nargs="*", help="Lista explícita de arquivos .LCO")
    ap.add_argument("--saida", help="Arquivo de saída do relatório (opcional; "
                                     "por padrão imprime no terminal)")
    args = ap.parse_args()

    caminhos = []
    if args.dir:
        caminhos.extend(coletar_arquivos(args.dir))
    if args.arquivos:
        caminhos.extend(args.arquivos)

    if not caminhos:
        print("Nenhum arquivo informado. Use --dir ou --arquivos.", file=sys.stderr)
        sys.exit(1)

    dados_por_tabela = defaultdict(list)
    erros_layout = []
    nao_reconhecidos = []

    for caminho in caminhos:
        tabela = identificar_tabela(caminho)
        if not tabela:
            nao_reconhecidos.append(caminho)
            continue
        validar_arquivo(caminho, tabela, dados_por_tabela, erros_layout)

    # garante que tabelas que não tiveram nenhum arquivo enviado fiquem
    # como None (para as regras não acusarem falsa dependência quando o
    # jurisdicionado simplesmente não enviou aquele arquivo neste lote)
    dados_final = {}
    for tabela in TABLE_SCHEMAS:
        if tabela in dados_por_tabela:
            dados_final[tabela] = dados_por_tabela[tabela]
        else:
            dados_final[tabela] = None

    erros_regras = rodar_todas_regras(dados_final)

    linhas_saida = []
    linhas_saida.append("=" * 78)
    linhas_saida.append("VALIDADOR SIM — BLOCO DE CONTRATAÇÕES (Tabelas 501 a 513)")
    linhas_saida.append("Manual do SIM 2026 — TCE-CE")
    linhas_saida.append("=" * 78)
    linhas_saida.append("")

    if nao_reconhecidos:
        linhas_saida.append("ARQUIVOS NÃO RECONHECIDOS (prefixo fora do padrão LI/PE/CL/MC/LT/TL/DL/CO/CT):")
        for c in nao_reconhecidos:
            linhas_saida.append(f"  - {c}")
        linhas_saida.append("")

    linhas_saida.append(f"Arquivos processados: {len(caminhos) - len(nao_reconhecidos)}")
    for tabela in TABLE_SCHEMAS:
        n = len(dados_por_tabela.get(tabela, []))
        status = f"{n} registro(s)" if tabela in dados_por_tabela else "não enviado neste lote"
        linhas_saida.append(f"  Tabela {tabela}: {status}")
    linhas_saida.append("")

    linhas_saida.append("-" * 78)
    linhas_saida.append(f"ERROS DE LAYOUT (tipo/tamanho/domínio/obrigatoriedade): {len(erros_layout)}")
    linhas_saida.append("-" * 78)
    if erros_layout:
        linhas_saida.extend(erros_layout)
    else:
        linhas_saida.append("Nenhum erro de layout encontrado.")
    linhas_saida.append("")

    linhas_saida.append("-" * 78)
    linhas_saida.append(f"ERROS DE REGRAS DE NEGÓCIO / INTEGRIDADE REFERENCIAL: {len(erros_regras)}")
    linhas_saida.append("-" * 78)
    if erros_regras:
        linhas_saida.extend(erros_regras)
    else:
        linhas_saida.append("Nenhum erro de regra de negócio encontrado.")
    linhas_saida.append("")

    total = len(erros_layout) + len(erros_regras)
    linhas_saida.append("=" * 78)
    linhas_saida.append(f"TOTAL DE OCORRÊNCIAS: {total}")
    linhas_saida.append("=" * 78)

    saida_texto = "\n".join(linhas_saida)

    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(saida_texto)
        print(f"Relatório salvo em: {args.saida}")
    else:
        print(saida_texto)

    sys.exit(1 if total > 0 else 0)


if __name__ == "__main__":
    main()
