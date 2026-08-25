# Validador SIM — Bloco de Contratações (Tabelas 501 a 513)

Valida arquivos-texto do SIM (Manual do SIM 2026, TCE-CE) referentes aos
itens **5.3.27 a 5.3.35**:

| Tabela | Nome                                                    | Arquivo   |
|--------|----------------------------------------------------------|-----------|
| 501    | Processos Administrativos para Contratações              | `LI*.LCO` |
| 502    | Publicações de Processos Adm. para Contratações           | `PE*.LCO` |
| 503    | Tipos de Responsáveis pela Contratação                     | `CL*.LCO` |
| 504    | Identificação dos Responsáveis pela Contratação            | `MC*.LCO` |
| 505    | Licitantes e Fornecedores de Bens e Serviços                | `LT*.LCO` |
| 506    | Itens que Compõem os Bens ou Serviços                        | `TL*.LCO` |
| 507    | Dotações Utilizadas para Contratações                       | `DL*.LCO` |
| 511    | Contratos                                                 | `CO*.LCO` |
| 513    | Contratados                                               | `CT*.LCO` |

## O que é validado

### 1. Layout de campos (por registro/linha)
- **Tipo** (numérico x caractere) e **formato** (ex.: decimais com ponto).
- **Tamanho** (exato ou "até N posições", conforme cada campo).
- **Obrigatoriedade** (campo não pode ficar vazio quando exigido).
- **Domínio de valores** (ex.: Espécie do Processo só aceita
  N/F/D/I/R/P/C/Q/M; Modalidade do Contrato só aceita
  OR/AA/AR/AP/PA/PR/RE etc.).
- Confere se o **campo 1 (Tipo do Documento)** de cada linha bate com o
  tipo esperado para aquele arquivo.

Campos opcionais que, segundo o Manual, devem ser preenchidos com um
valor "sentinela" quando não se aplicam (ex.: `""` ou `0`) — como os
campos de licitação numa Dispensa, ou os campos de obra num contrato
que não é de engenharia — **não** são penalizados quando corretamente
preenchidos com esse sentinela.

### 2. Regras de negócio e integridade referencial entre tabelas
- **501**: consistência entre Espécie do Processo (campo 5) e o
  preenchimento condicional dos blocos "Dados de Licitação" (16-20,
  31, 32) x "Dados de Dispensa/Inexigibilidade/Adesão" (21-24) — itens
  e.7/e.8; exigência de Órgão Gerenciador da Ata para Adesão (e.11);
  consistência do campo Sistema de Registro de Preços para Adesão
  (e.15); tamanho dos IDs PNCP (e.16/e.17); menção a
  Lei/Artigo/Decreto no campo de Fundamentação Legal (e.9).
- **502, 505, 506, 507**: o processo referenciado (Data de Autuação +
  Número do Processo) deve existir na Tabela 501.
- **503 → 504**: o Responsável (504) deve referenciar um registro
  existente de Tipo de Responsável (503); e a própria 501 (campos
  10/11/12) deve apontar para um registro em 503.
- **505 → 506**: o vencedor identificado nos campos 11/12 da 506 deve
  existir como Licitante/Fornecedor na 505 para o mesmo processo.
- **511**: regras de Contrato Original x Aditivo (e.2 a e.6) —
  Aditivo precisa referenciar Contrato Original existente; Aditivo de
  Prazo puro ("AP") deve ter valor 0.00; Aditivos que alteram valor
  devem ser positivos; campos de obra (15-18) só preenchidos quando
  Tipo de Objeto = "E"; campos de processo (20/21) preenchidos de
  forma consistente (e.8).
- **511 → 513**: Contratado deve referenciar um Contrato existente na
  511.

## Uso

```bash
# Validar todos os arquivos .LCO de uma pasta
python validador_sim.py --dir /caminho/da/pasta

# Validar arquivos específicos
python validador_sim.py --arquivos LI202601.LCO CO202601.LCO CT202601.LCO

# Salvar relatório em arquivo
python validador_sim.py --dir /caminho/da/pasta --saida relatorio.txt
```

O programa retorna código de saída `0` se não houver nenhuma
ocorrência, e `1` caso existam erros (útil para uso em pipelines/CI).

## Estrutura do projeto

```
validador_sim/
├── schemas.py          # especificação campo a campo de cada tabela (501-513)
├── parser.py           # leitura/parse dos arquivos + validação de layout
├── regras.py           # regras de negócio e integridade referencial
├── validador_sim.py    # CLI principal
├── exemplo_dados/            # lote de exemplo 100% válido (0 ocorrências)
└── exemplo_dados_com_erros/  # mesmo lote com 4 erros propositais (para teste)
```

## Limitações importantes

- O validador funciona **por lote** (arquivos de um mesmo mês/UG
  informados juntos). Se um arquivo referenciado (ex.: a Tabela 501)
  não for informado no lote, o validador **não** acusa erro de
  integridade referencial — assume que o registro já foi enviado ao
  TCE em remessa anterior, como o próprio Manual permite (envios
  fracionados). Se você quiser validação retroativa completa,
  seria necessário alimentar o validador com o histórico completo
  já enviado (ex.: lendo de um banco de dados local espelhando o
  SIM), não apenas o lote do mês corrente.
- Regras que dependem de outras tabelas fora do escopo 501-513 (ex.:
  validar se o CPF do responsável realmente consta na Tabela 951 —
  Agentes Públicos Municipais, ou se o Elemento de Despesa da Tabela
  507 existe na Tabela 204) não foram implementadas aqui, pois fogem
  do escopo solicitado (501 a 513). Posso estender o validador para
  cobrir essas dependências também, se você quiser.
- Este validador reproduz as regras de layout e as observações (e.x)
  descritas no Manual, mas não substitui o **PGI oficial do TCE-CE**,
  que é a ferramenta homologada para efetivamente gerar o ofício e
  liberar o envio da prestação de contas.
