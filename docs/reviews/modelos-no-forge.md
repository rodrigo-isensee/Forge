---
tipo: review
contrato: 1
pedido: modelos-no-forge
branch: melhoria/modelos-no-forge
commit: 29872420a29449ce52785a6448158c973236ebf6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Parecer de code review: modelos de parecer achados no repositório do Forge

Escopo: `1008338..2987242` (5 arquivos: `agents/tech-lead.md`, `agents/qa-engineer.md`, `templates/projeto/docs/security/_modelo.md`, `tests/test_modelos_citados.py`, fragmento `changelog.d/modelos-no-forge.md`). Revisão completa (primeira rodada). O Forge não tem `docs/engineering/praticas.md`; pelo pedido, vale como sem regras de prática.

## Achados
- A1 (bloqueante) tests/test_modelos_citados.py:49 · caminho em variável foge do MapaCobreOQueOsTestesLeem; o mapa do bin/forge-testes não leva a test_modelos_citados (mudar agents/*.md ou os _modelo.md dá dirigido sem ele). Pôr o módulo no CONTEUDO e voltar aos literais.

## Leitura
- E1 (agentes): a cláusula nas linhas 16 de `agents/tech-lead.md` e 20 de `agents/qa-engineer.md` segue a opção A do desenho, só acrescenta texto e continua valendo para os projetos (o caminho `docs/<tipo>/_modelo.md` vem primeiro). Sem efeito em invariantes de `tests/config.json`.
- E2 (teste): os três testes pegam a falha. Sondas numa cópia em `$TMPDIR` (`git archive` do HEAD revisado): o original passa (3 OK); sem a cláusula em `agents/qa-engineer.md`, 2 falhas (o teste de existência e o da cláusula); com uma linha a mais no modelo de segurança do template, 1 falha (o teste de igualdade). O teste que percorre os agentes afirma um mínimo (`achados >= 2`). A regex exige crase antes de `docs/`, então não confunde com a citação `templates/projeto/docs/...`.
- MODELO-SEGURANCA-DERIVA: o template recebe a frase que só a raiz tinha; agora as duas cópias são iguais e o `expectedFailure` foi retirado.
- Commits: quatro, Conventional Commits em português, um por mudança coerente; o fragmento do changelog está no formato.

## Parecer
Reprovado por A1, que se corrige com pouco esforço.

A1, explicação. `bin/forge-testes` é ferramenta de iteração, não portão (`docs/economia-de-tokens.md`, regra 5; o CI e o pre-push rodam a suíte inteira). Então o furo não deixa passar nada para a `develop`. Mesmo assim, o teste `MapaCobreOQueOsTestesLeem` existe justamente para que o mapa não minta, e montar o caminho em variável para não ser pego por ele é contornar uma checagem (`R-CONFORMIDADE`); o próprio commit `53a334b` diz isso no título. Planejei o modo dirigido para `agents/tech-lead.md`, `agents/qa-engineer.md`, `docs/security/_modelo.md` e `templates/projeto/docs/security/_modelo.md`: os quatro dão `dirigido` sem `test_modelos_citados`. Quem itera numa mudança desses arquivos recebe verde local e só vê a quebra no CI. Correção: incluir `test_modelos_citados` na tupla `CONTEUDO` de `bin/forge-testes:45` (alcança `agents/`, `stacks/`, `docs/` e, por `PUBLICADO`, `templates/`), escrever o teste de igualdade com literais `RAIZ / "docs/security/_modelo.md"` e `RAIZ / "templates/projeto/docs/security/_modelo.md"` e apagar o comentário das linhas 47 e 48. Mudar o mapa roda a suíte completa (`ALTERA_O_MAPA`). Isso fecha o cartão FTM-MAPA-MODELOS na mesma volta: é a mesma descoberta e está no mesmo estágio (decisão do dono de 2026-10-21 00:10).

Recomendações (não bloqueiam):
- `tests/test_modelos_citados.py:8-9`: há duas linhas em branco entre `CITACAO` e `CLAUSULA`; basta uma.
- ARCH-MODELO-CITADO (`agents/software-architect.md:20`, que cita `docs/architecture/features/_modelo.md` sem a cláusula) é o mesmo problema num terceiro agente. Pela mesma decisão do dono, cabe trazê-lo nesta volta: acrescentar a cláusula e incluir o agente no conjunto `CLAUSULA`. Fica a critério do Jarvis.

Segurança: o parecer próprio é do `security-engineer` (`docs/security/modelos-no-forge.md`); não o refiz.
