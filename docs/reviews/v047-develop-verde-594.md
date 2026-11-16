---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde-594
commit: 3932b52db16af1e0d21fdbc2a122a8ce01b77635
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.447), conserto na develop do que o #594 quebrou (PR 603)

Escopo: `git diff 58dfa2ab...3932b52d`, 12 arquivos, +36/-41. Código e teste que contam (M14): `bin/forge-testes` 10 e `tests/*.py` 15 linhas, dentro do teto. Uma classe de comportamento: o mapa do `bin/forge-testes` para spec de mutantes, mais specs realinhadas e o `self.env` do `ConferirTodas`.

## Achados
- A1 (recomendado) tests/mutantes/v046-ci-lote-e1.json:36 · M4 (parte [1..5]) e a retirada do I96/I97 seguem a develop com o #576; a branch melhoria/v047-verde-0472 junta isto ao revert do #576, que volta ci.yml a [1, 2, 3] e as guardas de suite-partes.py:120-121: realinhe M4 e devolva I96/I97 lá (AR-12).
- A2 (recomendado) .github/pull_request_template.md:1 · o corpo do PR 603 não tem `## Projeto de origem` nem `## Como medir` e a catraca reprova por isso (R-CONTRIB); preencha antes do merge.

## Sondas

## Parecer
Aprovado no 3932b52d.

- Cartão (E2.416): faz o que pede. O mapa leva a spec ao `test_forge_mutante`, que roda `test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` sobre a raiz; spec ilegível ou sem teste segue na suíte completa (`if da_spec else None`). O `ConferirTodas` usa `self.env`, o que `test_ambiente_git` exige. As specs M34, M2, M3, M4 e RP-M1 seguem a fonte atual; I96 e I97 saem porque as linhas já não existem em `scripts/suite-partes.py` na develop.
- Guarda nova (`bin/forge-testes:320`): mutante T8 declarado em `tests/mutantes/v047-specs-conferidas.json` (8 mutantes, no limite). Rodei o mutante à mão: com `if True`, `MapaDosNovos.test_spec_ilegivel_sem_teste_ou_com_teste_de_fora_segue_na_completa` falha (7 falhas), morreu. Teste do ramo de falha por comportamento, não por texto da fonte.
- Ferramentas: `forge-mutante --conferir --base 58dfa2ab` diz que o trecho de cada spec do diff está no lugar; `--cobertura --base 58dfa2ab` dá `bin/forge-testes:320` coberta pelo T8. `--conferir --todas` na raiz sai 1 com 31 linhas de specs antigas, todas fora deste diff e cobertas pela catraca `tests/fixtures/mutantes-pendentes.txt`.
- Testes do item: `python3 -m unittest tests.test_testes_tocados tests.test_forge_mutante.ConferirTodas tests.test_ambiente_git` rodou 185 testes, OK (skipped=1).
- CI do PR 603 no head 3932b52d: vermelho, mas nenhum teste do diff falha. Falham, nas duas versões do Python, `test_metricas_texto` (agents/jarvis.md), `test_reval_delta` (ci.yml e docs/propostas/), `test_orcamento_instrucao` (devops-engineer), `test_catraca.Workflows` (2) e `test_frontmatter_agentes` (agents/jarvis.md): arquivos que este item não toca, vindos da develop (merges de 15:08 a 15:42); a E2.438 os junta. `bateria (pareceres)` espera os pareceres da classe; a catraca está no A2.
- Checklist: nomes e comentários claros; sem custo (R-CUSTO), sem termo de projeto (R-NEUTRO); commits em Conventional Commits, um por mudança; fragmento em `changelog.d/`. AR-12 volta neste pedido (specs desalinhadas por merges paralelos): contagem atualizada em `docs/engineering/achados-recorrentes.md`.
