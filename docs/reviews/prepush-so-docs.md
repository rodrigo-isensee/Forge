---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/prepush-so-docs
commit: 0ba1a876f9176c74d9dae97ca208805c3f652e43
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: prepush-so-docs (versao-033, L03, E18 PREPUSH-SO-DOCS)

Revisor: `forge:tech-lead`, outra instância (não é o autor; D-ETAPAS-INST = A). Base `928e61b66015f7ee2a2e585dc8178e07dc16be39`, dois commits (`669798a`, `0ba1a87`).

## Achados
- A1 (recomendado) tests/test_prepush_so_docs.py:206 · o teste de "sem variável que pule" testa três nomes fixos (lista negativa, classe AR-3); a garantia real é o hook não ler variável nova; conferir no texto do hook que so_docs só lê os campos do stdin seria mais forte.
- A2 (recomendado) templates/projeto/.githooks/pre-push:46 · o teste de remote_sha zerado não mata a mutação que tira esta linha (o git diff com sha zerado falha e já roda tudo); é defesa em profundidade, declare como equivalente na spec de mutantes se a mutação a listar.
- A3 (recomendado) tests/test_prepush_so_docs.py:1 · o item ocupa dois commits e o primeiro não se reverte sozinho (revert de 669798a dá conflito UD no teste); os dois juntos revertem limpo; o merge por squash na develop junta o item num commit só.

## Leitura
- Limite exato da seção E18 do modelo de ameaças: o `pre-push.local` só é pulado quando todas as refs enviadas mudam só `docs/*` ou `*.md` (sensível a caixa). `.github/` é recusado antes do teste de `.md`, então `.github/x.md` roda tudo: mais estrito que o limite, coerente com "inclusive `.github/`".
- C-1: o diff é `git diff --name-only -z --no-renames <remote_sha> <local_sha>` por ref, nunca a árvore (`test_diff_usa_os_commits_e_nao_a_arvore`); qualquer ref fora do critério roda tudo (`test_duas_refs_uma_docs_outra_codigo_roda`).
- C-2: branch nova, tag, apagar ref (sozinha ou junto de ref só docs), falha do git (git falso), objeto ausente e diff vazio rodam tudo; `mktemp` que falha também roda tudo.
- C-3: `a.MD`, `a.md.ts`, `docsx/`, `Docs/`, `docs` como arquivo, `LICENSE`, `.txt` e imagem rodam tudo; o renome `src/a.ts` para `docs/a.ts` lista o nome antigo e roda tudo.
- C-4: as checagens R-VERIFY e da `main` (linhas 4 a 29) não mudaram (`test_main_segue_bloqueada`); o `unset GIT_DIR` vem antes do primeiro git novo; a linha do pulo é a do modelo; o `pre-push.local` recebe o stdin já consumido, como antes.
- T-1 a T-4: nenhuma variável, opção ou arquivo de configuração novo; critério não alargado; `.githooks/pre-push` do Forge e o CI do modelo intocados.
- Casos pedidos no brief: só docs, misto, `.github/`, renomeado, removido e branch nova estão no teste, que roda o hook de verdade num repositório descartável com `sem_manutencao` e sem herdar `GIT_*` (AR-4 conferido).
- Mapa do `bin/forge-testes`: `templates/projeto/.githooks/pre-push` passa a listar `test_prepush_so_docs` junto do conjunto publicado (conferido com `bin/forge-testes --listar`).
- Fragmento `changelog.d/prepush-so-docs.md` presente, marcado como afrouxa; o rótulo `afrouxa-regra` é do dono (E1.8). R-NEUTRO e R-CUSTO: nada específico de projeto nem pago.
- Teto M14: 265 linhas de código e teste (hook 33, teste 230, mapa 1), fora de `hooks/` e de `PROTEGIDOS`; dispensado pela DECISÃO DO DONO "B" de 2026-11-03 10:06 (lotes por área, com rótulo afrouxa-regra). Um comportamento só.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-3 (lista negativa, A1, só no teste), AR-4 e AR-6 (o `2>/dev/null` do git diff não esconde falha: a falha roda tudo) conferidos.

## Ferramentas
- Testes do item: `python3 -m unittest tests.test_prepush_so_docs tests.test_ambiente_git tests.test_testes_tocados`, "Ran 130 tests in 45.196s, OK".
- `shellcheck templates/projeto/.githooks/pre-push`: pendência, o `shellcheck` não está instalado nesta máquina ("command not found"); fica com o CI do PR, que o roda na bateria.
- Suíte inteira: não rodada aqui (D-5); fica com o `qa-engineer` e o CI.
- Segurança e devops: pareceres próprios (E1.4, E1.5), não refeitos aqui.

## Parecer
Aprovado. O hook cumpre o limite exato e os controles C-1 a C-5 da seção E18, sem nenhuma mudança proibida, e o teste cobre a matriz pedida. Os três achados são recomendações e não devolvem a entrega.
