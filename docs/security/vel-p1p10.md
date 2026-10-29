---
tipo: revisao-seguranca
contrato: 1
pedido: vel-p1p10
branch: melhoria/vel-p1p10
commit: 9e191c78b4dbed14aa439122ade1f86bcb955a57
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: vel-p1p10

Escopo: diff `a55ec03...9e191c7` (revalidação por delta do parecer a513ad9, que valeu sobre 0b4585f; antes `3b94791...0b4585f`) (teto de 150 linhas por PR e um comportamento por entrega; mutante equivalente declarado e até 16 mutantes por spec no `bin/forge-mutante`; verificadores do autor antes do push).

## Gatilhos
`R-SEGURANCA`, controles do Forge: `bin/forge-mutante` produz a evidência de mutação que o QA usa (`R-QA`). O texto de agentes e skills (teto M14, verificadores do autor) só estreita regra: 400 para 150 linhas e um comportamento por PR, sem portão retirado.

Conferido, com sonda própria fora da worktree (fixtures de `tests/test_forge_mutante.py`, repositório de brinquedo):
- sobrevivente não declarado ao lado de um equivalente válido: rc 1 (`M3 · sobreviveu` e `equivalente: E1 · ...`);
- sobrevivente ao lado de um equivalente com o `de` ausente: rc 2;
- equivalente sem justificativa, com menos de 20 caracteres, `None`, número, ou com `testes` junto: spec recusada antes de rodar, rc 2 (testes do item e sonda);
- equivalente em arquivo de teste, com `../`, `/etc/...`, `.git/config` ou `-x`: recusado por `validar_caminho`, rc 2;
- o equivalente lê o arquivo só por `git show <sha>:<caminho>` (objeto do commit): link simbólico versionado devolve o texto do alvo, sem seguir o link; nada é lido fora da worktree nem escrito na árvore;
- `MAXIMO_DE_MUTANTES = 16`: 17 mutantes recusados antes de rodar; o pior caso de tempo continua limitado por `--prazo` (até 3600 s por execução).
- `python3 -m unittest tests.test_forge_mutante`: 67 testes, OK.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 (máscara do shell) não se aplica, o diff não toca shell.

## Revalidação por delta (9e191c7)
- `bin/forge-mutante` idêntico ao de 0b4585f (`git diff 0b4585f..9e191c7 -- bin/forge-mutante` vazio): as sondas do parecer a513ad9 seguem valendo sem mudança; `tests.test_forge_mutante` 67 testes OK e `tests.test_forge.TetoPorPr` 6 testes OK na worktree.
- Volta 2 (8757265..cf04778): uma linha de `skills/qa-testing/SKILL.md:85` (8 para 16) e um teste em `tests/test_forge.py`; texto e teste, nenhum controle; fecha a R4 abaixo.
- Merge da develop a55ec03: `git diff a55ec03..9e191c7 --stat` lista só arquivos do lote (agentes, skills, `bin/forge-mutante`, testes, pareceres); `.githooks/`, `hooks/` e `bin/forge-check` da develop chegam sem alteração do lote, com parecer próprio na develop, e não abrem caminho novo para o forge-mutante.
- PA-7: AR-1 (máscara do shell) não se aplica ao diff (sem shell); AR-9 (`limite-antigo-no-texto`, linha da skill) fechada pela volta 2.
- O parecer a513ad9 segue valendo: veredito `aprovado` mantido, sem bloqueante novo.

## Achados

## Detalhe dos achados
Sem bloqueante. Recomendações, sem caminho de ataque que vença um portão (a spec é versionada, do autor, e o QA lê a rodada):

- R1 · `bin/forge-mutante:466` · no `--cobertura`, o mutante equivalente conta como `coberta · ... · declarado, não provado`, igual ao mutante com teste (sonda: rc 0). O autor pode "cobrir" uma condição nova com um equivalente sem teste, e a saída não distingue. A rodada da spec mostra a linha `equivalente:`, então o QA ainda vê. Severidade baixa. Correção mínima: imprimir `equivalente · <arquivo>:<linha> · <spec>:<id>` para esse caso (ou tratá-lo como `isenta`). Esforço P. Dono: tech-lead.
- R2 · `bin/forge-mutante:37` · a docstring segue dizendo `0 = todos morreram`; uma spec só de equivalentes sai 0 sem rodar teste nenhum (sonda). Correção mínima: `0 = todos morreram ou são equivalentes declarados`, e, se o time quiser fechar, exigir ao menos um mutante com `testes` por rodada. Esforço P. Dono: tech-lead.
- R3 · `bin/forge-mutante:243` e `:273` · a justificativa aceita 20 caracteres com espaço interno (`a` + 18 espaços + `b`) e sequência de escape ANSI (sonda: `\x1b[1A\x1b[2K` passa e sai na linha, e num terminal pode apagar a linha de cima e simular `M9 · morreu`). Correção mínima: contar `len("".join(j.split())) >= 20`, como as `isentas`, e recusar `not j.isprintable()`. Severidade baixa. Esforço P. Dono: tech-lead.
- R4 (fechada em cf04778) · `skills/qa-testing/SKILL.md:85` · a mesma frase que passou para 3 a 16 mutantes ainda diz "Pedido com mais de 8 mutantes divide"; o lado errado é o conservador (divide antes do preciso), sem efeito de segurança. Correção mínima: trocar 8 por 16. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, testes do item e sonda local; `shellcheck` presente e não aplicável (sem shell no diff). Lacunas no PATH: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` (o diff não toca workflow nem dependência; nenhum segredo visto na leitura).
