---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: bdd44bc03d942aa8e119a16db562def9d3eb9a43
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E122.13), corte do G1.2 sozinho no head bdd44bc0

Revisão completa única do commit bdd44bc0 sobre a base 5cff9f6a (develop). Ele recorta o G1.2 (revalidação só no delta) da melhoria/v0480-g1-2-3, aprovada no head 17c4ba57 (review 0319158a, E122.7).

## Achados
- A1 (recomendado) bin/forge-check:4164 · herdado do A7 da g1-2-3: a repetição é reconhecida só por (id, arquivo), então um bloqueante novo no mesmo arquivo com um id antigo passa fora do delta. Vira cartão; meça nos pareceres recusados antes de apertar.

## Sondas

## Parecer
Aprovado.

**O corte bate com o código revisado.** Comparei o patch de cada arquivo com o patch revisado (merge-base 7c4ee3c1..17c4ba57):
- Sem nenhuma diferença: `agents/qa-engineer.md`, `agents/security-engineer.md`, `agents/tech-lead.md`, `bin/forge-testes`, `docs/regras/R-REVIEW.md`, `tests/test_parecer_fora_do_delta.py`, `tests/test_testes_tocados.py` e `tests/mutantes/v047-docs-pareceres-2.json` (M11).
- Em `bin/forge-check`, o bloco G1.2 inteiro é idêntico ao de 17c4ba57: constantes, `mesmo_commit`, `parecer_anterior`, `trechos_do_delta` e `fora_do_delta`. As chamadas em `cmd_docs` (`:480`) e em `cmd_pr` (`:2045`) também são as mesmas.
- Mutantes: FD1 a FD22, FL1 e FL2. Só o campo `pedido` muda. Os de G1.3 (CT*, MQ*, BR*, HD*, FM1, BA1) ficaram de fora.

**O corte não leva nada do G1.3.**
- No diff não aparecem `so_texto_ou_so_teste`, `barreiras_do_leve` nem `cabecalho_do_md`, e `classe_das_mudancas` não foi tocada.
- `isencoes_do_diff` e `isencoes_da_entrega` (M13) continuam como na base, que é o certo enquanto o G1.3 não entra.
- Os arquivos que só o G1.3 tocava ficaram fora: `hooks/parecer.py`, `docs/hooks.md`, `R-QA.md`, `test_classe_risco`, `test_isencoes` e as fixtures do hook.
- A frase "a T (G1.3), não" saiu de `R-SEGURANCA.md:13`, e a linha da T saiu de `rigor-por-classe.md`. O que ficou nos dois é só o G1.2 e o encurtamento do `verificada_por`, que já estavam aprovados.
- `R-SEGURANCA.md:17` mantém o "que volta e é corrigida" (A1 da 1.ª rodada da g1-2-3).
- Em `tests/pesos-d4.json`, só entra o `test_parecer_fora_do_delta`. Os pesos de `test_classe_risco` e `test_isencoes`, que são do G1.3, não vieram.

**Tamanho (H1):** 65 linhas de código em `bin/forge-check` e 1 em `bin/forge-testes`, dentro do teto, para um comportamento só.

**Classe:** `forge-check classe --base 5cff9f6a` dá C, com os pareceres de review, qa e revisao-seguranca (gatilho `docs/regras/`).

**Changelog:** o fragmento `changelog.d/v0480-g1-2-delta.md` traz o critério de reversão (2 escapes em 14 dias).

**Verificadores rodados no head bdd44bc0:**
- Testes dos arquivos tocados, `python3 -m unittest tests.test_parecer_fora_do_delta tests.test_testes_tocados`: 217 testes, OK. 1 pulado pelo sandbox (namespace de pid).
- `bin/forge-mutante --cobertura --base 5cff9f6a`: rc=0. Toda guarda mudada de `bin/forge-check` (4134 a 4172) tem mutante declarado.
- `bin/forge-mutante --base 5cff9f6a --processos 1`, uma chamada por pedido: 24 de 24 mortos em v0480-g1-2-delta e M9 a M13 mortos em v047, sem sobrevivente.
- Suíte completa: fica com o CI do PR, que ainda não foi aberto.
