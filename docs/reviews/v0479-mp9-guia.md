---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 2054ef3b3ea3a7996b8e9dedbcf71fbb5782a089
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E24.2, MP9 guia "vários projetos")

Diff `0c47762a..2054ef3b`: README (seção nova, 8 linhas), `templates/projeto/CLAUDE.md` (1 linha em `## Sessão`), fragmento `changelog.d/v0479-mp9-guia.md`, teste novo `tests/test_guia_varios_projetos.py` e a citação `teste-le` em `tests/test_reval_delta.py`. Só documentação e teste: sem código de controle, sem guarda mudada, teto H1 não se aplica.

Conferido contra o desenho (`multi-projeto-1711.md`, linha MP9) e contra o código: `PESO_MAXIMO = 10` e `peso_valido` (0 exclusive a 10, fora disso 1) em `hooks/agentes.py:190,222`; empréstimo da vaga parada em `hooks/agentes.py:238-277`; escape `FORGE_CARGA_LIVRE=1` só com um projeto em `hooks/agentes.py:1079-1088` (MP5); `forge-status --maquina` em `bin/forge-status:90`; `Projeto: <nome>`, `[<projeto>]` e "para qual projeto?" em `skills/falar-com-o-dono/varios-projetos.md`. O guia diz o que o código faz. O teste amarra o "até 10" do texto ao `PESO_MAXIMO` do hook, o que impede o guia de envelhecer em silêncio.

`docs/engineering/praticas.md` não tem regra "decidida por: leitura"; nada a citar de ferramenta. R-NEUTRO: sem termo de projeto. Suíte: só no CI do PR (R-REVIEW); rodado o teste do diff: `python3 -m unittest test_guia_varios_projetos test_reval_delta` (em `tests/`), 14 testes, OK.

## Achados
- A1 (recomendado) tests/test_reval_delta.py:140 · a linha nova carrega, depois do comentário MP9, a cópia do comentário da linha anterior ("v047 E2.222: o teste lê o README..."), que não descreve este teste; apague o resto colado.

## Parecer
Aprovado. O guia cobre as cinco partes do MP9 (janela por projeto no modo auto, teto em partes iguais com `peso` e comando pronto, escape só com um projeto, bot único com `[<projeto>]`, `forge-status --maquina`), bate com o código e tem teste que acusa a seção ausente e a faixa do `peso` divergente. A1 é cosmético e não devolve.
