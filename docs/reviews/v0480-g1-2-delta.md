---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 4182040651ad42a57cd8d047c4684946efbf659d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E140.4), revalidação por delta do #812 no head 41820406

Revalidação por delta depois do merge da develop (216413c9) na branch, com conflito em `bin/forge-testes`. O parecer anterior é a revisão completa do corte G1.2 no head bdd44bc0 (E122.13), aprovada; o texto dele segue abaixo, em "Parecer anterior".

## Achados
- A1 (recomendado) bin/forge-check:4164 · herdado do A7 da g1-2-3: a repetição é reconhecida só por (id, arquivo), então um bloqueante novo no mesmo arquivo com um id antigo passa fora do delta. Vira cartão; meça nos pareceres recusados antes de apertar.

## Revalidação (head 41820406)
**Delta lido:** `forge-check parecer delta docs/reviews/v0480-g1-2-delta.md`, intervalo bdd44bc0..41820406, sem o que veio da base. No domínio: `bin/forge-check`, `bin/forge-testes` e `tests/pesos-d4.json`. Em `bin/forge-check` e em `tests/pesos-d4.json`, o delta só traz o que veio da develop (`autorizacao gravar` do #810, `test_fechar_busca_pareceres`, `test_forge_copia_nome`), já revisado nos PRs de origem. Saída: `revalida: sim (bin/forge-testes mudou depois do parecer)`.

**Resolução do conflito em `bin/forge-testes`:** a tupla `FORGE_CHECK` (linha 160) ficou com os dois itens, `test_autorizacao_gravar` (da develop) e `test_parecer_fora_do_delta` (da branch). Cada um aparece uma vez, e os dois arquivos de teste existem. As linhas do `MAPA` que vieram da develop (`bin/forge-copia`, `test_fechar_busca_pareceres`) entraram sem conflito.

**O patch da branch não mudou com o merge.** Comparei, arquivo por arquivo, as linhas mudadas de `5cff9f6a..bdd44bc0` (o patch revisado) com as de `216413c9..41820406`. Os 16 arquivos de código, teste, regra e mutante são iguais. Em `bin/forge-testes`, a única mudança da branch sobre a develop continua sendo o acréscimo de `test_parecer_fora_do_delta` na tupla, a mesma linha revisada. O H1 não muda.

**Verificadores no head 41820406:**
- Testes dos arquivos tocados, `python3 -m unittest tests.test_testes_tocados tests.test_parecer_fora_do_delta`: 217 testes, OK. 1 pulado pelo sandbox.
- `bin/forge-testes --listar bin/forge-testes` pede a suíte completa, porque o arquivo muda o mapa; ela fica com o CI do PR #812.
- O merge não mudou nenhuma guarda, então não há mutante novo.

## Parecer
Aprovado.

### Parecer anterior (head bdd44bc0)
**O corte bate com o código revisado.** Comparei o patch de cada arquivo com o patch revisado (merge-base 7c4ee3c1..17c4ba57):
- Sem nenhuma diferença: `agents/qa-engineer.md`, `agents/security-engineer.md`, `agents/tech-lead.md`, `bin/forge-testes`, `docs/regras/R-REVIEW.md`, `tests/test_parecer_fora_do_delta.py`, `tests/test_testes_tocados.py` e `tests/mutantes/v047-docs-pareceres-2.json`.
- Em `bin/forge-check`, o bloco G1.2 inteiro é idêntico ao de 17c4ba57: constantes, `mesmo_commit`, `parecer_anterior`, `trechos_do_delta` e `fora_do_delta`. As chamadas em `cmd_docs` (`:480`) e em `cmd_pr` (`:2045`) também são as mesmas.
- Mutantes: os 24 do G1.2, em `tests/mutantes/v0480-g1-2-delta*.json` (três arquivos de 8), vieram iguais aos revisados; só o campo `pedido` muda. Os do G1.3 ficaram de fora.

**O corte não leva nada do G1.3.**
- No diff não aparecem `so_texto_ou_so_teste`, `barreiras_do_leve` nem `cabecalho_do_md`, e `classe_das_mudancas` não foi tocada.
- `isencoes_do_diff` e `isencoes_da_entrega` continuam como na base, que é o certo enquanto o G1.3 não entra.
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
- `bin/forge-mutante --base 5cff9f6a --processos 1`, uma chamada por pedido: todos os 24 de v0480-g1-2-delta e os de v047 tocados no diff mortos, sem sobrevivente.
- Suíte completa: fica com o CI do PR.
