---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-validar-yaml-workflow
commit: d7a8c8f9e4508668b497477e1283b08ae0322fb5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 · validador de YAML dos workflows (E13.6, PR #967)

1ª rodada completa (E13.17) no head d7a8c8f9, base a1971853.

## Escopo conferido
- Diff: `scripts/validar-yaml-workflow.py` (77 linhas, só biblioteca padrão), `tests/test_validar_yaml_workflow.py` (13 testes), `tests/mutantes/v048-validar-yaml-workflow.json` (14 mutantes), fragmento `changelog.d/`.
- Tamanho (H1): 77 linhas de código, um comportamento (validar o subconjunto de YAML); dentro do teto.
- Fora do item por corte declarado no pedido (E13.6, histórico 13:44): encaixe no `.githooks/pre-push` (PREPUSH-VALIDA-YAML) e verde só com obrigatórios em `bin/forge-fechar` (VERDE-SO-COM-OBRIGATORIOS), como cartões.
- R-CUSTO: nada pago, nada de rede; R-NEUTRO: nada de projeto.

## O defeito do #929 e os workflows de hoje
- O `ci.yml` do envio 385a268a (o reprovado pelo devops em 26/11 23:17, run 45924102244 sem jobs) acusa exatamente a linha 360 (`name: Fumaça no Python 3.14 (F6: ...)`), rc 1, e nada mais.
- Os 5 workflows do head (`catraca.yml`, `ci.yml`, `diario.yml`, `obsoletas.yml`, `release.yml`): rc 0, saída vazia.
- Sondas próprias sem falso positivo: `branches: [a]`, `run: echo a:b`, URL `http://x.y/z`, `${{ x }}`, `'a: b'`, comentário com `:`, a mesma chave em `with:` de itens diferentes; e o corpo `>` seguido de `b: c: d` acusa a linha de fora do bloco.

## Verificação local (só o diff)
- `python3 -m unittest tests.test_validar_yaml_workflow`: 13 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v048-validar-yaml-workflow.json`: 14 de 14 morreram (M2, M10 e M11 por erro do teste); `--cobertura --base a1971853`: toda condição do diff coberta; `--conferir --base a1971853`: trechos no lugar.
- CI do head (run 46166823206): vermelho; `suíte (python 3.12, parte 4/5)` falhou em `tests/test_indice_forge.py` (:41, :50, :65): `docs/indice-forge.md` sem a linha de `validar-yaml-workflow.py`. Reproduzido local: `python3 -m unittest tests.test_indice_forge`, 3 falhas. As demais partes e baterias do run, verdes.

## Achados
- A1 (bloqueante) docs/indice-forge.md:1 · índice derivado não regenerado: o script novo em scripts/ não tem linha no índice e test_indice_forge cai (CI parte 4/5 e local, 3 falhas); rode scripts/gerar-derivados.py (ou scripts/indice-forge.py) e commite o índice, como pede a definição de pronto
- A2 (recomendado) changelog.d/v048-validar-yaml-workflow.md:2 · o fragmento lista "aspas" entre o que o validador confere, mas o script não confere aspas (a docstring, linha 9, diz que valor entre aspas não tem o conteúdo conferido); tirar "aspas" do texto
- A3 (recomendado) tests/test_validar_yaml_workflow.py:77 · os três subprocessos (77, 84, 89) chamam o Python sem `-I` e herdam o ambiente; a prática do Forge para teste com subprocesso é ambiente limpo e `-I`, para PYTHONPATH ou PYTHONSTARTUP do ambiente não alcançarem o script

## Sondas
- S1 · python3 -m unittest tests.test_indice_forge (head d7a8c8f9) · espera: OK · obtido: FAILED (failures=3), docs/indice-forge.md desatualizado

## Parecer
Reprovado pelo A1: o CI do head está vermelho porque o índice derivado (`docs/indice-forge.md`) não foi regenerado; correção mecânica do autor. No mérito, o validador faz o que o E13.6 pede dentro do corte declarado: pega o defeito real do #929 na linha certa e não acusa nada nos 5 workflows de hoje; o código é curto, legível, sem dependência, com saída e códigos de retorno documentados. A2 e A3 são recomendados: texto do changelog e higiene dos subprocessos do teste.

M2, M10 e M11 morrerem por erro e o mutante `break` em `if not par:` sobreviver são achados do parecer de QA (`docs/qa/v048-validar-yaml-workflow.md`, A1 bloqueante e A2), não repetidos aqui; conferi que o teste de chave repetida cai com o mutante semântico `... and False` (retorno vazio), logo a lacuna do M2 é do mutante, não do teste. A correção do A1 do QA entra antes deste parecer ser revalidado pelo delta.
