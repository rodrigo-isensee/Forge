---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-cobertura-p5p6
commit: 82aebd68f49603053581e6d6ea12f98d8beec3e9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.429), COBERTURA-ESTUDO P5 e P6

Escopo revisado: `1b88640e...82aebd68` (1 commit), `docs/engineering/praticas.md` (novo), `tests/test_modelos_projeto.py` (classe `PraticasDoForge`) e o fragmento `changelog.d/v047-cobertura-p5p6.md`. Parecer completo, porque não havia parecer anterior.

## Achados
- A1 (recomendado) tests/test_modelos_projeto.py:182 · a regra do shellcheck (docs/engineering/praticas.md:13) cita o passo "shellcheck (scripts e hooks)", mas o teste só confere que `.github/workflows/ci.yml` existe. Se o passo for renomeado, o teste segue verde. Sugestão: conferir também que o nome entre aspas aparece no workflow.

## Sondas

## Parecer
**Aprovado.**

- Requisito: a DECISÃO DO DONO de 2026-11-16 (pedido v047, "C4 P5 e P6"; "C3 só se não aumentar o tempo do CI do PR; meça antes") está cumprida. A P5 virou a tabela "quem decide" no `praticas.md` do Forge, com a cobertura registrada como pendência até a C3. A P6 já estava na develop: o passo do CI escolhe os arquivos pelo shebang (`ci.yml:653-666`, CHANGELOG 0.43.2). A entrega não promete mais do que isso.
- Fatos conferidos no head: os 10 caminhos citados existem. O job "cobertura (informativa)" só roda no push na `main` (`ci.yml:117-122`) e não reprova nada. `Neutralidade` e `NeutralidadeDoNucleo` existem em `tests/test_forge.py:436,473`.
- Testes: rodei `python3 -m unittest tests.test_modelos_projeto` aqui, com 20 testes OK. Também mutei o `praticas.md` três vezes, e o `PraticasDoForge` falhou em todas: caminho inexistente (`tests/catraca_nao.py`), cobertura trocada de "pendência" para "leitura" e regra "ferramenta" sem caminho do repositório. O teste não roda subprocesso, então AR-4 e AR-5 não se aplicam.
- Mutantes (AR-1, AR-2, AR-12): o diff não toca código de controle (`bin/`, `hooks/`, `scripts/`). Os `if` estão dentro do próprio teste, então não há guarda a declarar.
- Suíte: não a rerrodei (R-REVIEW). Vale o CI do PR.
- Tamanho (M14): 42 linhas de código e teste contadas, um comportamento só.
- Segurança: o diff só tem documentação e um teste de leitura de texto, sem gatilho.
