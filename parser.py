# -*- coding: utf-8 -*-
"""
Parser e validador GENÉRICO de campos para os arquivos-texto do SIM,
conforme especificações do item 4.5 do Manual do SIM 2026:

  - Campos separados por vírgula, sem espaços entre a vírgula e o conteúdo.
  - Campos caractere entre aspas duplas.
  - Campos numéricos SEM aspas; decimais com ponto separando parte inteira
    e decimal (ex.: 20000.00).
  - Cada linha = 1 registro.
"""

import csv
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from schemas import FieldSpec

NUM_RE_INT = re.compile(r"^-?\d+$")
NUM_RE_DEC = re.compile(r"^-?\d+\.\d+$")


@dataclass
class FieldError:
    linha: int
    campo_idx: int
    campo_nome: str
    valor: str
    mensagem: str


@dataclass
class ParsedRecord:
    linha: int
    raw: List[str]
    tabela: str


def parse_line(raw_line: str) -> List[str]:
    """
    Faz o parse de uma linha do arquivo SIM.
    Formato: campos caractere entre aspas, campos numéricos "nus",
    tudo separado por vírgula (sem espaços).
    Usamos csv.reader com quotechar='"' para lidar corretamente com
    vírgulas dentro de campos de texto entre aspas.
    """
    raw_line = raw_line.rstrip("\r\n")
    if raw_line == "":
        return []
    reader = csv.reader([raw_line], delimiter=",", quotechar='"',
                         skipinitialspace=False, strict=False)
    return next(reader)


def read_sim_file(path: str) -> List[ParsedRecord]:
    records = []
    with open(path, "r", encoding="latin-1", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            if not line.strip():
                continue
            fields = parse_line(line)
            tabela = fields[0].strip() if fields else ""
            records.append(ParsedRecord(linha=i, raw=fields, tabela=tabela))
    return records


def _is_sentinela(spec: FieldSpec, valor: str) -> bool:
    """
    Campos marcados como 'required=False' no schema representam campos que,
    segundo o Manual, devem ser preenchidos com um valor padrão de
    'não aplicável' quando a condição da tabela não se aplica ao registro
    (ex.: campos de licitação quando a espécie é Dispensa; campos de obra
    quando o contrato não é de Obra/Serviço de Engenharia; datas/CPFs que
    só existem em caso de Aditivo, etc.). Nesses casos o valor sentinela
    (vazio para caractere, "0"/"0.00" para numérico) é o CORRETO e não
    deve ser penalizado pelas checagens de tamanho exato/tipo.
    """
    if spec.required:
        return False
    if spec.kind == "C":
        return valor == ""
    else:  # numérico
        return valor in ("", "0", "0.00")


def _validar_tamanho(spec: FieldSpec, valor: str) -> Optional[str]:
    if spec.kind == "C":
        n = len(valor)
        if spec.exact and n != spec.size:
            return (f"tamanho inválido: esperado exatamente {spec.size} posições, "
                    f"recebido {n}")
        if not spec.exact and n > spec.size:
            return f"tamanho inválido: máximo {spec.size} posições, recebido {n}"
    else:  # numérico
        # separa parte inteira/decimal se houver
        if spec.decimals:
            if "." in valor:
                ipart, dpart = valor.split(".", 1)
            else:
                ipart, dpart = valor, ""
            ipart_digits = ipart.lstrip("-")
            if len(ipart_digits) > spec.size:
                return (f"parte inteira excede {spec.size} posições "
                        f"(recebido {len(ipart_digits)})")
            if len(dpart) > spec.decimals:
                return (f"parte decimal excede {spec.decimals} posições "
                        f"(recebido {len(dpart)})")
        else:
            digits = valor.lstrip("-")
            if spec.exact and len(digits) != spec.size:
                return (f"tamanho inválido: esperado exatamente {spec.size} dígitos, "
                        f"recebido {len(digits)}")
            if not spec.exact and len(digits) > spec.size:
                return f"tamanho inválido: máximo {spec.size} dígitos, recebido {len(digits)}"
    return None


def _validar_tipo(spec: FieldSpec, valor: str) -> Optional[str]:
    if spec.kind == "N":
        if spec.decimals:
            if not (NUM_RE_INT.match(valor) or NUM_RE_DEC.match(valor)):
                return (f"formato numérico inválido (esperado inteiro ou decimal "
                        f"com ponto, ex.: 12345.67): '{valor}'")
        else:
            if not NUM_RE_INT.match(valor):
                return f"formato numérico inválido (esperado somente dígitos): '{valor}'"
    return None


def _validar_obrigatoriedade(spec: FieldSpec, valor: str) -> Optional[str]:
    if spec.required:
        if spec.kind == "C" and valor.strip() == "":
            return "campo obrigatório não pode ser vazio"
        if spec.kind == "N" and valor.strip() == "":
            return "campo obrigatório não pode ser vazio"
    return None


def _validar_dominio(spec: FieldSpec, valor: str) -> Optional[str]:
    if spec.allowed is not None:
        # campos "required=False" com nota de sentinela podem vir vazios/zero
        if valor == "" or valor == "0":
            if not spec.required:
                return None
        if valor not in spec.allowed:
            opcoes = "/".join(spec.allowed)
            return f"valor '{valor}' fora do domínio permitido ({opcoes})"
    return None


def validar_campos_registro(schema: List[FieldSpec], raw: List[str],
                             linha: int) -> List[FieldError]:
    erros: List[FieldError] = []

    n_esperado = len(schema)
    n_recebido = len(raw)
    if n_recebido != n_esperado:
        erros.append(FieldError(
            linha=linha, campo_idx=0, campo_nome="(registro)",
            valor="", mensagem=(f"número de campos incorreto: esperado {n_esperado}, "
                                 f"recebido {n_recebido}")))
        # ainda assim tenta validar os campos que existem, até o menor tamanho
    for spec in schema:
        pos = spec.idx - 1
        if pos >= len(raw):
            continue
        valor = raw[pos]

        # obrigatoriedade é sempre verificada primeiro
        msg = _validar_obrigatoriedade(spec, valor)
        if msg:
            erros.append(FieldError(
                linha=linha, campo_idx=spec.idx, campo_nome=spec.name,
                valor=valor, mensagem=msg))

        # se o campo é opcional e está com o valor-sentinela ("" ou 0),
        # este é o preenchimento CORRETO para "não aplicável" — não faz
        # sentido aplicar checagens de tamanho exato/tipo/domínio sobre ele
        if _is_sentinela(spec, valor):
            continue

        for fn in (_validar_tipo, _validar_tamanho, _validar_dominio):
            msg = fn(spec, valor)
            if msg:
                erros.append(FieldError(
                    linha=linha, campo_idx=spec.idx, campo_nome=spec.name,
                    valor=valor, mensagem=msg))
    return erros
