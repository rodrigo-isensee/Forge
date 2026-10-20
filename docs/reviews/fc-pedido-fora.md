---
tipo: review
contrato: 1
pedido: fc-pedido-fora
branch: melhoria/fc-pedido-fora
commit: 37b531f8dc936905206a2469a1957919024e077b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Code review: FC-PEDIDO-FORA (E1.3)

Rodada 1, diff inteiro `50997b7..37b531f` (2 commits, 6 arquivos, 149+/10-). Revisor é outra instância do tech-lead, não a autora (D-ETAPAS-INST). Segurança (E1.4) tem parecer próprio do `security-engineer` em `docs/security/`; não refeito aqui.

Ferramentas rodadas em 37b531f: `python3 -m unittest tests.test_pedido_fora tests.test_conferencia_registrar tests.test_sobreposicao_quadro` → `Ran 38 tests ... OK`. Vermelho na develop: `tests/test_pedido_fora.py` da branch contra `bin/` e `tests/` de 50997b7 (cópia por `git archive` em `$TMPDIR`) → `Ran 8 tests ... FAILED (failures=6)` (os 4 de leitura fora do repositório e os 2 subtestes de recusa sem KANBAN.md; os 2 que passam são o de travessia, que a develop já recusava, e o de "com KANBAN nada muda"). `git diff --quiet 50997b7 37b531f -- tests/config.json` → rc 0 (nenhum invariante saiu). Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o autor relatou 959 OK e validar-plugin OK, o QA refaz no head). O Forge não tem `docs/engineering/praticas.md`, então não há regra "ferramenta" a citar; o checklist da skill `engineering-practices` foi aplicado por leitura.

## Achados

## Detalhe dos achados
Conferência pedida no brief:
- **E1 contra o desenho do arquiteto · cumpre.** `caminho_do_pedido` (`bin/forge-check:631-643`) procura, nesta ordem fixa, o caminho dado, a cópia principal, a raiz e, por último, cada `RAIZES_DE_BRIEF`, este último via `dentro_da_raiz` restrito a `docs/pedidos` (`realpath`). `cmd_brief_conferir` (`:2735-2740`) e `cmd_brief_gerar` (`:2784`) passam a usar `caminho_do_pedido`; o brief tenta `Path(arquivo)` e depois `caminho_de_brief`, restrito a `docs/briefs`. `linha_de_origem` (`:646-656`) só informa (entra como `(linha, False)`, nunca reprova) e só para arquivo em `docs/pedidos/` ou `docs/briefs/` de uma raiz de brief.
- **Ordem fixa e a raiz vence · cumpre.** No pedido, as raízes do repositório vêm antes do laço de `RAIZES_DE_BRIEF`. No brief, `caminho_de_brief` (`:883-891`) monta os válidos na ordem `(raiz, *RAIZES_DE_BRIEF)` e devolve o primeiro que existe; a raiz existe → ela vence; nenhum existe → o primeiro (a raiz), como antes. `test_mesmo_nome_nas_duas_raizes_a_raiz_do_repositorio_vence` cobre o pedido.
- **E2 · cumpre.** `cmd_movimento` (`:1170`) e `cmd_conferencia_registrar` (`:1215`) checam `KANBAN.md` antes de qualquer `mkdir`, devolvem a mensagem `SEM_QUADRO` (aponta a raiz e `--raiz`) e o chamador sai com rc 1. Só aperta: nada novo é gravado. O quadro real do Forge (`~/.forge-contrib/KANBAN.md`) existe, então o uso com `--raiz ~/.forge-contrib` segue funcionando; a sessão no `~/Forge`, sem KANBAN.md, deixa de criar `docs/kanban/` ali, que é o defeito do pedido.
- **E3, os casos do desenho · cumprem, e testam comportamento.** 8 testes em `tests/test_pedido_fora.py` cobrem os 7 casos: leitura de pedido e brief na raiz de brief com `origem:`; pedido absoluto com brief relativo; `brief gerar` (afirma o `Pedido:` tirado do conteúdo); `entrega` pelo id (rc 2 na conferência das refs, ou seja, passou da leitura); travessia (`../segredo`, `../../docs/segredo`, `docs/outro.md`, `../../x.md`) e link para fora (`elo` em `docs/pedidos` e em `docs/briefs`) recusados com rc 2 e sem `origem:`; raiz vence; e o E2 em dois (sem KANBAN: rc 1, árvore idêntica antes e depois e `docs/kanban` inexistente; com KANBAN: os dois arquivos criados). HOME falso em tmp (`Raiz.rodar`), como no desenho. Os textos procurados pelos testes de ausência existem no código (`brief: não consegui ler`, `entrega: não consegui ler o pedido`). `setUp` de `tests/test_sobreposicao_quadro.py` e de `tests/test_conferencia_registrar.py` gravam KANBAN.md.
- **Mudança de contrato documentada · cumpre.** `docs/transcricoes.md:32` descreve a recusa sem KANBAN.md dos dois comandos e a busca em `~/.forge-contrib` com a linha `origem:`; fragmento `changelog.d/fc-pedido-fora.md` em `### Corrigido`.
- **Invariantes e regras · cumpre.** `tests/config.json` intocado; nenhum texto de regra copiado; R-NEUTRO (só caminhos genéricos), R-CUSTO (sem rede nem serviço).
- **Commits · cumpre.** Dois commits Conventional Commits em português, `fix` (código e testes) e `docs`.

Recomendações (não bloqueiam; ficam para o autor ou um cartão):
- R1 (recomendado) `bin/forge-check:883` · a troca em `caminho_de_brief` vale para todos os chamadores, não só para o `brief`: `gerar_volta` (`:944`, `--volta`), `conferir_volta` (`:1024`, `Volta-de:`) e `--anterior` (`:2752`) passam a achar `docs/briefs/x.md` relativo em `~/.forge-contrib` quando falta na raiz (antes só o caminho absoluto chegava lá). É o efeito querido (pré-requisito da DV-2), mas não tem teste nem frase em `docs/transcricoes.md`; sugestão: um subTest com `Volta-de: docs/briefs/<n>.md` relativo só na raiz de brief, e a frase.
- R2 (recomendado) `tests/test_pedido_fora.py:70` · o caso "raiz vence" só cobre o pedido; falta o brief de mesmo nome nas duas raízes (o ramo novo de `caminho_de_brief`). E o teste afirma só a ausência de `origem:`; afirmar também `rc in (0, 1)` e a ausência de `não consegui ler` fecha o caso de a leitura falhar por outro motivo.
- R3 (recomendado) `skills/kanban-scrum/SKILL.md:64` e `agents/jarvis.md:46` · descrevem o `forge-check movimento` sem a recusa nova; o texto não ficou falso, mas quem roda fora da raiz do projeto só descobre pela mensagem. Sugestão: "(na raiz do projeto, com KANBAN.md, ou com `--raiz`)".
- Nota, fora do diff: o primeiro laço de `caminho_do_pedido` (cópia principal e raiz) não passa por `dentro_da_raiz`, então `--pedido ../x` ainda sai de `docs/pedidos/` dentro do repositório. É anterior a esta mudança e não cresceu aqui; deixo para o `security-engineer` decidir se vira cartão.
