---
tipo: qa
contrato: 1
pedido: transcricoes-conformidade
branch: melhoria/transcricoes-conformidade
commit: ec39104
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA - propriedades de conformidade do verificador de transcrições

Links: `docs/transcricoes.md`, CHANGELOG `[Não publicado]`, ADR 0009 seção 8.

## Escopo
Suíte, validação do plugin, catraca, todas as fixtures de `tests/transcricoes/` e um teste de aceitação local com uma transcrição real anonimizada (nada versionado).

## Cenários e resultados
| ID | Cenário | Resultado |
|---|---|---|
| CT-01 | `python3 -m unittest discover -s tests` | passou: 172 testes, OK |
| CT-02 | `claude plugin validate . --strict` | passou |
| CT-03 | `python3 tests/catraca.py --base origin/develop` | **falhou** (saída 1): 2 achados R-CUSTO em `bin/forge-check` (ver BUG-01) |
| CT-04 | Fixtures `ok`, `contorno-ok`, `copia-ok`, `custo-ok`, `decisao-ok`, `papel-ok`, `sandbox-ok`, `verify-script-ok` | passou: saída 0, sem linhas |
| CT-05 | `viola-teto`, `viola-main` | violou como esperado (R-TETO; 2x R-MAIN) |
| CT-06 | `papel-viola` | violou: 5x R-CONFORMIDADE.papel (pr create, docs/reviews, .claude, merge, pacote) |
| CT-07 | `contorno-viola` | violou: 3x contorno (script, outra ferramenta, outro agente), 2x R-VERIFY, 1x papel |
| CT-08 | `sandbox-viola`, `copia-viola`, `custo-viola`, `verify-script-viola` | violou: 1x sandbox, 1x R-COPIA, 3x R-CUSTO, 1x R-VERIFY (script com 2 flags) |
| CT-09 | `decisao-viola`, `decisao-opcoes` | aviso R-DECISAO com saída 0, como especificado |
| CT-10 | Aceitação: anonimizar a sessão real mais recente | gerou 251 linhas; grep de e-mail, `/home/`, usuário e nome de projeto: 0 ocorrências. As únicas ocorrências do termo "forge" são tipos de agente `forge:*` (esperado) |
| CT-11 | Aceitação: `verificar --teto 5` | 1 saída 1; contagens abaixo |

## Aceitação com sessão real (contagens)
Eventos: 151 cmd, 47 agente, 45 fim, 5 bloqueio, 1 escrita, 1 resposta, 0 sandbox, 0 com `ator` (sem sidechain nesse arquivo).

| Tipo | Qtde | Avaliação |
|---|---|---|
| R-QA | 15 | verdadeiros em parte: a sessão abriu PRs de várias entregas, e a aproximação "sessão inteira" só vê delegação anterior; parte antes da primeira delegação ao QA. Ruído esperado em sessão longa, documentado em "O que é verificado" |
| R-REVIEW | 4 | idem, mesma aproximação |
| PROMPT-PADRAO | 14 | delegações sem as seis seções; plausível (prompts curtos), não conferi conteúdo |
| R-VERIFY | 3 | todos `core.hooksPath` (ativação do hook da fábrica, uso legítimo documentado em CLAUDE.md); falso positivo de política na prática, já que o próprio fluxo manda ativar |
| R-CONFORMIDADE.papel | 1 | escrita em `docs/regras/` pela sessão principal (`jarvis`), fora da matriz (tech-lead, doc); plausível verdadeiro positivo |
| contorno / sandbox / R-TETO / R-MAIN / R-COPIA / R-CUSTO / R-DECISAO | 0 | sem achados. R-DECISAO só olha a última mensagem, e há 1 `resposta` com 0 perguntas |

Observação: R-VERIFY `core.hooksPath` dispara em ativação legítima; considerar distinguir `git config core.hooksPath .githooks` (apontar para a pasta do repo) de desativação (valor vazio ou outro caminho). Não classificado como bug por estar descrito na especificação como regra, mas gera ruído.

## Bugs
### BUG-01 - catraca falha com R-CUSTO em `bin/forge-check` (alta)
- Responsável sugerido: dev (autor do verificador); autorização do usuário necessária se a saída for `custo_permitido`.
- Passos: `python3 tests/catraca.py --base origin/develop` em ec39104.
- Esperado: saída 0.
- Obtido: saída 1. `claude-print` em `bin/forge-check:502` (literal `cmd("custo claude -p", ...)`) e `url-de-api-paga` em `bin/forge-check:310` (lista `DOMINIOS_PAGOS`). Na `develop` (a5aa9b4) a catraca passa, então o PR seria barrado no CI (ADR 0008, portões valem para todos).
- Correção possível: montar os literais sem o padrão (dados em `hooks/conformidade.json`) ou incluir em `custo_permitido` de `tests/config.json` com autorização explícita do usuário (docs/regras/R-CUSTO.md).

## Dados de teste
Fixtures de `tests/transcricoes/`; sessão real anonimizada em diretório temporário, removida ao fim. Nenhum conteúdo da transcrição foi copiado para este parecer.

## Resultado
Parecer reprovado por BUG-01 (alto, aberto). Demais cenários passaram. Unitários: 172 OK.
