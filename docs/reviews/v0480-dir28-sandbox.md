---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-dir28-sandbox
commit: 4568c9b7276e6aa2edcbb4818e7ef09c08253aeb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E151.2, PR #847, diretriz 28 no Jarvis)

## Escopo lido
Diff `e15c8566..4568c9b7` (1 commit, 5 arquivos): `agents/jarvis.md`, `skills/falar-com-o-dono/nao-trava.md`,
`tests/fixtures/diretrizes-do-dono.json`, `tests/test_jarvis_nucleo.py`, `changelog.d/v0480-dir28-sandbox.md`.
Só documentação e teste; nenhuma linha de guarda de código mudou, sem mutante a declarar.

## Conferências
- **Diretriz 28 no agente:** a linha "Pedido de decisões" do `agents/jarvis.md` traz a regra (conferir o sandbox no primeiro
  comando; se falhar, parar e dar ao dono o comando de reabrir) antes do "Leia `.../nao-trava.md`"; o detalhe (modo
  automático, exemplo do erro, comando `jarvis` ou `claude --agent forge:jarvis --permission-mode auto`, o dono nunca aprova
  comando a comando) está em `nao-trava.md` e bate com a linha 11 de `templates/projeto/CLAUDE.md`.
- **Diretriz 25 (nada some, o detalhe muda de lugar):** o que saiu das duas linhas encurtadas segue nas skills:
  `Projeto: <nome>` na primeira linha (`varios-projetos.md:11`), confirmar o projeto (`varios-projetos.md:13`), `[<projeto>]`
  no Telegram (`varios-projetos.md:17`); marcas, tags e cartões em `skills/fluxo-do-pedido/SKILL.md:29`; critérios em
  `skills/produto-criterios/SKILL.md`. O Jarvis segue mandando ler `varios-projetos.md`, `fluxo-do-pedido` e `produto-criterios`.
- **Invariantes do Jarvis:** nenhum trecho de `invariantes["agents/jarvis.md"]` (`tests/config.json`) estava nos trechos
  removidos; `tests.test_forge.RegrasInviolaveis` verde (3 testes).
- **Tabela de diretrizes:** 28 passa de `pendente` a `fabrica` com o trecho exato do agente; `MAX_PENDENTES` 8 → 7 só desce,
  com o motivo no comentário.
- **Testes dos arquivos tocados** (sem suíte local, pelo brief): `tests.test_jarvis_nucleo` e `tests.test_guia_varios_projetos`
  verdes (49 testes); `tests.test_forge.Referencias`, `Neutralidade` e `NeutralidadeDoNucleo` verdes (10 testes). O teste novo
  `SandboxNoPrimeiroComando` confere a regra na linha certa e a ordem (regra antes do caminho do detalhe).
- **CI do PR #847:** no momento do parecer, `bateria (pareceres)`, `instalação (python 3.14)` e `árvore já provada na develop`
  verdes; `bateria` e `catraca` pendentes. O merge espera o CI verde (`R-FLUXO`).
- **Commit e changelog:** mensagem em Conventional Commits, em português, com o motivo do encurtamento; fragmento em
  `changelog.d/` no formato.

## Parecer
Aprovado. A mudança faz o que a etapa E151.1 pede, sem regra perdida (diretriz 25), sem subir o teto do núcleo e com teste
de presença e de ordem.
