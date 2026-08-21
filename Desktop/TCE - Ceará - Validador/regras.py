# -*- coding: utf-8 -*-
"""
Regras de negócio e de integridade referencial entre as tabelas
501, 502, 503, 504, 505, 506, 507, 511 e 513, extraídas das seções
"Características" (itens a-e) de cada tabela no Manual do SIM 2026.

Cada função recebe o dicionário {tabela: [ParsedRecord, ...]} já
parseado e devolve uma lista de strings de erro/alerta.
"""

from typing import Dict, List
from parser import ParsedRecord


def _key_processo(raw):
    """Chave (Data Autuação, Número Processo) -> campos 3 e 4 na maioria das tabelas."""
    return (raw[2], raw[3])


def _get(raw, idx1based, default=""):
    pos = idx1based - 1
    return raw[pos] if pos < len(raw) else default


def checar_501(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    erros = []
    for rec in dados.get("501", []):
        raw = rec.raw
        especie = _get(raw, 5)
        licit_fields = {
            16: _get(raw, 16), 17: _get(raw, 17), 18: _get(raw, 18),
            19: _get(raw, 19), 20: _get(raw, 20), 31: _get(raw, 31),
            32: _get(raw, 32),
        }
        disp_fields = {
            21: _get(raw, 21), 22: _get(raw, 22), 23: _get(raw, 23), 24: _get(raw, 24),
        }
        is_sentinela_licit = (
            licit_fields[16] == "" and licit_fields[17] in ("0", "")
            and licit_fields[18] == "9" and licit_fields[19] == "9"
            and licit_fields[20] in ("0", "0.00") and licit_fields[31] == ""
            and licit_fields[32] == ""
        )
        is_sentinela_disp = all(v == "" for v in disp_fields.values())

        if especie == "N":  # Processo Licitatório -> e.7: campos de licitação devem estar preenchidos
            if is_sentinela_licit:
                erros.append(
                    f"[501] linha {rec.linha}: Espécie 'N' (Licitatório) mas campos "
                    f"16-20/31/32 (dados de licitação) estão com valores padrão de "
                    f"'não aplicável' — verificar item e.7.")
            if not is_sentinela_disp:
                erros.append(
                    f"[501] linha {rec.linha}: Espécie 'N' (Licitatório) mas campos "
                    f"21-24 (dispensa/inexigibilidade) deveriam estar em branco "
                    f"(\"\") — verificar item e.8.")
        elif especie in ("F", "D", "I", "R"):  # Dispensa/Inexigib./Adesão -> e.8
            if is_sentinela_disp:
                erros.append(
                    f"[501] linha {rec.linha}: Espécie '{especie}' (Dispensa/"
                    f"Inexigibilidade/Adesão) mas campos 21-24 estão em branco — "
                    f"verificar item e.8.")
            if not is_sentinela_licit:
                erros.append(
                    f"[501] linha {rec.linha}: Espécie '{especie}' mas campos "
                    f"16-20/31/32 (dados de licitação) não estão com os valores "
                    f"padrão de 'não aplicável' (\"\", 0, \"9\", \"9\", 0, \"\", \"\") "
                    f"— verificar item e.7.")
            if especie == "R" and _get(raw, 24) == "":
                erros.append(
                    f"[501] linha {rec.linha}: Espécie 'R' (Adesão a Ata de Registro "
                    f"de Preços) exige o campo 24 (Órgão Gerenciador da Ata) "
                    f"preenchido.")
            if especie == "R" and _get(raw, 33) != "N":
                erros.append(
                    f"[501] linha {rec.linha}: Espécie 'R' (Adesão a Ata) — campo 33 "
                    f"(Sistema de Registro de Preços) deve ser 'N', pois a Ata é "
                    f"pré-existente e gerada por outro órgão — verificar item e.15.")

        # e.9 — fundamentação legal deve conter algo que pareça lei/artigo quando não vazio
        fund = _get(raw, 23)
        if fund and not any(t in fund.lower() for t in ["lei", "art", "decreto", "resolução",
                                                          "resolucao", "regulamento"]):
            erros.append(
                f"[501] linha {rec.linha}: campo 23 (Fundamentação Legal) preenchido "
                f"mas não menciona 'Lei/Artigo/Decreto/Resolução' — confira item e.9 "
                f"(deve identificar Número da Lei, Artigo, Parágrafo, Inciso).")

        # e.16/e.17 — tamanho estrito dos IDs PNCP quando preenchidos
        idc = _get(raw, 34)
        if idc and len(idc) != 25:
            erros.append(
                f"[501] linha {rec.linha}: campo 34 (Id Contratação PNCP) preenchido "
                f"com {len(idc)} caracteres — deve ter exatamente 25 (ou \"\").")
        idata = _get(raw, 35)
        if idata and len(idata) != 31:
            erros.append(
                f"[501] linha {rec.linha}: campo 35 (Id Ata PNCP) preenchido com "
                f"{len(idata)} caracteres — deve ter exatamente 31 (ou \"\").")
    return erros


def _index_501(dados) -> set:
    return {_key_processo(r.raw) for r in dados.get("501", [])}


def checar_dependencia_de_501(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    """502, 505, 506, 507 exigem processo já cadastrado na 501 (mesmo lote ou anteriormente)."""
    erros = []
    processos_501 = _index_501(dados)
    for tabela, campo_nome in [("502", "Publicações"), ("505", "Licitantes/Fornecedores"),
                                ("506", "Itens"), ("507", "Dotações")]:
        for rec in dados.get(tabela, []):
            chave = _key_processo(rec.raw)
            if chave not in processos_501 and dados.get("501") is not None:
                erros.append(
                    f"[{tabela}] linha {rec.linha}: processo "
                    f"(Data Autuação={chave[0]}, Nº Processo={chave[1]}) não foi "
                    f"encontrado na Tabela 501 do mesmo lote — confirme se o "
                    f"processo já foi enviado ao TCE em remessa anterior (item e "
                    f"correlato de cada tabela).")
    return erros


def checar_503_504(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    """504 deve referenciar registro existente em 503 (campos 3,4,5)."""
    erros = []
    chaves_503 = {(_get(r.raw, 3), _get(r.raw, 4), _get(r.raw, 5))
                  for r in dados.get("503", [])}
    for rec in dados.get("504", []):
        chave = (_get(rec.raw, 3), _get(rec.raw, 4), _get(rec.raw, 5))
        if chave not in chaves_503 and dados.get("503") is not None:
            erros.append(
                f"[504] linha {rec.linha}: (CPF Gestor UG={chave[0]}, Data Portaria="
                f"{chave[1]}, Nº Sequencial={chave[2]}) não encontrado na Tabela 503 "
                f"— cadastre primeiro o Tipo de Responsável (503).")

    # 501 campos 10,11,12 também devem apontar para um registro em 503
    for rec in dados.get("501", []):
        chave = (_get(rec.raw, 10), _get(rec.raw, 11), _get(rec.raw, 12))
        if chave not in chaves_503 and dados.get("503") is not None:
            erros.append(
                f"[501] linha {rec.linha}: campos 10/11/12 (CPF Gestor UG/Data "
                f"Portaria/Nº Sequencial do Responsável pela Contratação) = {chave} "
                f"não encontrados na Tabela 503 — obrigatório existir previamente "
                f"(item e.5/501 e a) Descrição e Responsabilidade).")
    return erros


def checar_505_506(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    """506 campos 11,12 (vencedor) devem existir na 505 para o mesmo processo."""
    erros = []
    chaves_505 = {(_get(r.raw, 3), _get(r.raw, 4), _get(r.raw, 5), _get(r.raw, 6))
                  for r in dados.get("505", [])}
    for rec in dados.get("506", []):
        raw = rec.raw
        tipo_doc = _get(raw, 11)
        num_doc = _get(raw, 12)
        if tipo_doc == "" and num_doc == "":
            continue  # aceitável apenas se ainda não houver vencedor definido
        chave = (_get(raw, 3), _get(raw, 4), tipo_doc, num_doc)
        if chave not in chaves_505 and dados.get("505") is not None:
            erros.append(
                f"[506] linha {rec.linha}: Licitante/Fornecedor vencedor "
                f"(tipo={tipo_doc}, nº={num_doc}) não encontrado na Tabela 505 "
                f"para o mesmo processo — verifique item e.3/506.")
    return erros


def checar_511_513(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    erros = []

    # -- 511: regras de Original x Aditivo (e.2 a e.6) --
    contratos_originais = {}
    for rec in dados.get("511", []):
        raw = rec.raw
        modalidade = _get(raw, 7)
        if modalidade == "OR":
            chave = (_get(raw, 3), _get(raw, 4), _get(raw, 5))
            contratos_originais[chave] = rec

    for rec in dados.get("511", []):
        raw = rec.raw
        modalidade = _get(raw, 7)
        cpf_orig, num_orig, data_orig = _get(raw, 8), _get(raw, 9), _get(raw, 10)
        valor = _get(raw, 14)

        if modalidade == "OR":
            if not (cpf_orig == "" and num_orig == "" and data_orig == "0"):
                erros.append(
                    f"[511] linha {rec.linha}: Modalidade 'OR' (Original) mas campos "
                    f"8/9/10 não estão com os valores padrão (\"\",\"\",0) — "
                    f"verifique item e.3.")
        else:
            if cpf_orig == "" or num_orig == "" or data_orig == "0":
                erros.append(
                    f"[511] linha {rec.linha}: Aditivo '{modalidade}' precisa "
                    f"informar CPF/Nº/Data do Contrato Original nos campos 8/9/10 "
                    f"— verifique item e.3.")
            else:
                chave_orig = (cpf_orig, num_orig, data_orig)
                if chave_orig not in contratos_originais and dados.get("511") is not None:
                    erros.append(
                        f"[511] linha {rec.linha}: Aditivo '{modalidade}' referencia "
                        f"Contrato Original {chave_orig} que não foi encontrado como "
                        f"registro Modalidade='OR' no lote — confirme se o Original "
                        f"já foi enviado ao TCE.")

            if modalidade == "AP":  # Prazo apenas -> valor deve ser 0.00 (e.6)
                if valor != "0.00" and valor != "0":
                    erros.append(
                        f"[511] linha {rec.linha}: Aditivo 'AP' (só Prazo) deveria "
                        f"ter campo 14 (Valor Total do Contrato) = 0.00 — item e.6.")
            elif modalidade in ("AA", "AR", "PA", "PR", "RE"):  # altera valor -> deve ser > 0
                try:
                    if float(valor) <= 0:
                        erros.append(
                            f"[511] linha {rec.linha}: Aditivo '{modalidade}' altera "
                            f"valor do contrato — campo 14 deve ser positivo (mesmo "
                            f"para reduções) — item e.4.")
                except ValueError:
                    pass

        # e.7 — campos de obra (15-18) só preenchidos se Tipo de Objeto == 'E'
        tipo_objeto = _get(raw, 6)
        campos_obra = [_get(raw, 15), _get(raw, 16), _get(raw, 17), _get(raw, 18)]
        sentinela_obra = campos_obra[0] == "0" and campos_obra[1] == "" \
            and campos_obra[2] == "" and campos_obra[3] == "0"
        if tipo_objeto == "E" and sentinela_obra:
            erros.append(
                f"[511] linha {rec.linha}: Tipo de Objeto 'E' (Obra/Serviço de "
                f"Engenharia) mas campos 15-18 não foram preenchidos — item e.1/e.7.")
        if tipo_objeto != "E" and not sentinela_obra:
            erros.append(
                f"[511] linha {rec.linha}: Tipo de Objeto '{tipo_objeto}' (não é "
                f"Obra/Serviço de Engenharia) mas campos 15-18 estão preenchidos "
                f"— deveriam ser 0/\"\"/\"\"/0 — item e.1/e.7.")

        # e.8 — campos 20/21 (processo) só se oriundo de processo administrativo
        data_proc, num_proc = _get(raw, 20), _get(raw, 21)
        if (data_proc == "0") != (num_proc == ""):
            erros.append(
                f"[511] linha {rec.linha}: campos 20 (Data de Autuação) e 21 (Nº "
                f"Processo) inconsistentes — ambos devem estar preenchidos ou "
                f"ambos em branco/0 — item e.8.")

    # -- 513: deve referenciar contrato existente na 511 (campos 3,4,5) --
    chaves_511 = {(_get(r.raw, 3), _get(r.raw, 4), _get(r.raw, 5))
                  for r in dados.get("511", [])}
    for rec in dados.get("513", []):
        chave = (_get(rec.raw, 3), _get(rec.raw, 4), _get(rec.raw, 5))
        if chave not in chaves_511 and dados.get("511") is not None:
            erros.append(
                f"[513] linha {rec.linha}: Contrato (CPF Gestor={chave[0]}, "
                f"Nº Contrato={chave[1]}, Data={chave[2]}) não encontrado na "
                f"Tabela 511 — item e.1/513 (dados herdados de Contratos).")
    return erros


def checar_507_dotacao(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    """Checagens estruturais simples do Código de Projeto/Atividade x Número (item 507)."""
    erros = []
    for rec in dados.get("507", []):
        raw = rec.raw
        cod = _get(raw, 11)
        if cod == "9" and _get(raw, 12) not in ("", "000", "0"):
            erros.append(
                f"[507] linha {rec.linha}: código 9 (Reserva de Contingência) "
                f"normalmente não possui Número de Projeto/Atividade específico "
                f"— confira o campo 12.")
    return erros


def rodar_todas_regras(dados: Dict[str, List[ParsedRecord]]) -> List[str]:
    erros: List[str] = []
    erros += checar_501(dados)
    erros += checar_dependencia_de_501(dados)
    erros += checar_503_504(dados)
    erros += checar_505_506(dados)
    erros += checar_511_513(dados)
    erros += checar_507_dotacao(dados)
    return erros
