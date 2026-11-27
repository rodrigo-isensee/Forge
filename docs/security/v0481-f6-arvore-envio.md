---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: dcd4003c3bbb728d86c2e16a9df0aefad46a2036
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (PR #932, corte do envio do F6, volta 1, E32.35)

Volta por delta: `forge-check parecer delta` de `1567d509..dcd4003c`; no domínio, `scripts/arvore-testada.py` e `docs/protecao-de-branch.md` (relidos inteiros: `prova_do_pr` e `bateria_do_run_do_pr`, e o agregador `rapida` do `.github/workflows/ci.yml:174-199`, não tocado). Fora do domínio: specs de mutante -4 a -6 e `tests/test_arvore_testada.py`. Rodada anterior: aprovado, sem achados (fica no git).

Gatilhos: pipeline de CI (portão do push na develop), token do workflow, controle que afrouxa regra (R-FLUXO).

## Achados
- A1 (bloqueante) scripts/arvore-testada.py:181 · O run liga ao PR só por head_sha e head_branch: o run de OUTRO PR do mesmo ramo (base melhoria/y; testou o merge com outra base) prova o merge na develop, mesmo com o run do PR da develop vermelho. A doc (protecao-de-branch.md:31) promete base develop; o código não confere.

## Sondas
- S1 · python3 sonda_s1.py <cópia> (fixture do teste: run 555 do PR #77 com bateria failure; run 565 com pull_requests=[{number 999, base melhoria/y}] e bateria success) · espera: (False, ...) · obtido: (True, "árvore 1111111 igual à do head 3333333 do PR #77, run 565, job bateria")

## Detalhe dos achados
**A1.** Evidência: `scripts/arvore-testada.py:181-191` filtra os runs por evento, head_sha, path, repositório, status e `head_branch` e escolhe o maior `run_id`; nada liga o run à base do PR mesclado. O `ci.yml` roda em `pull_request` para qualquer base, e o passo "Nada pula degrau" só barra as bases `homolog` e `main` (`.github/workflows/ci.yml:519-523`): um PR `melhoria/x -> melhoria/y` roda a bateria inteira e pode ficar verde. O `compare base.sha...head` (`:192`) usa a base do PR da develop, não a do run, e não fecha o furo.

Caminho: quem tem escrita (agente ou colaborador) abre um segundo PR do mesmo ramo para um ramo com commits a mais (por exemplo, a correção que faz a bateria passar); o run desse PR, mais novo, fica verde sobre `merge(head, melhoria/y)`, árvore diferente da do head; o PR da develop é mesclado e o push na develop pula a suíte sem nunca ter testado a árvore mesclada. Ganho: a árvore não testada entra na develop com a `checagem rápida` verde, sem o vermelho do push que hoje a apanha depois. A S1 reproduz o caso, inclusive com o `pull_requests` do run dizendo que ele é de outro PR e de outra base (o PR empilhado segue aberto, então a API o lista), sinal que o código ignora.

As demais forjas pedidas fecham: fork (`head_repository.full_name` e `head.repo.full_name`), tentativa antiga (`run_attempt` do job), base velha (`compare` da develop anterior e da `base.sha` com o head, `behind` e `diverged` recusados), outro ramo no mesmo sha (`head_branch`).

Severidade: média (afrouxa o portão R-FLUXO pelo qual o rótulo `afrouxa-regra` foi aceito; a proteção da develop também lê o check `bateria` no mesmo sha, mas o corte tira a rede que pegaria o erro depois do merge). Correção mínima, as duas: (1) recusar o run cujo `pull_requests` não esteja vazio e não seja só o próprio PR (mesmo número e `base.ref` `develop`); (2) listar os PRs do ramo, `repos/<repo>/pulls?head=<dono>:<ramo>&state=all&per_page=100`, e não provar se algum, aberto ou fechado, tiver `base.ref` diferente de `develop` (cobre o PR empilhado já fechado, que some do `pull_requests`). Caso de abuso para o teste: run mais novo de PR do mesmo ramo com outra base, verde, e run do PR da develop vermelho, espera `(False, ...)`; e o mesmo com o PR empilhado fechado. Esforço: P. Dono: `devops-engineer` (script), `qa-engineer` (teste).

Doc: `docs/protecao-de-branch.md:31` está correta quanto à falha do próprio `arvore-envio` (o agregador sai vermelho, `ci.yml:194`); a frase "base `develop`" do run só passa a valer com a correção do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sonda S1 fora do repositório (usa a fixture de `tests/test_arvore_testada.py`, sem rede). Teste afetado rodado: `tests.test_arvore_testada` (31 testes, OK). CI do head `dcd4003c`: partes 1 a 5 da suíte, passos, verificações longas, instalação e `bateria (python 3.14)` verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhas pelo que falta da integração. `zizmor` e `actionlint` fora do PATH: lacuna.
