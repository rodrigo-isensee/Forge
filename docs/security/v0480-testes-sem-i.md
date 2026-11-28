---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-testes-sem-i
commit: 870f0b9157ad1953d2aa343be767e85b48ab0c34
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E161.4, testes sem -I na raiz, PR #845)

Base 789fc141, head 870f0b91. Delta: `skills/qa-testing/comandos.md`, `skills/qa-testing/SKILL.md`, `skills/briefs-e-conferencia/SKILL.md`, `skills/contribuir-com-o-forge/SKILL.md`, `tests/test_forge.py` (classe `RodarUmModuloComIsolamento`) e o fragmento do changelog. Nenhum arquivo de `bin/`, `scripts/`, `.githooks/`, `templates/`, `stacks/` nem `agents/` tocado (`git diff --stat` base..head).

## Gatilhos
Gatilhos: forma documentada de rodar teste (isolamento do interpretador no comando de topo; oráculo EXT-1 e PQ rodam por ela).

## Só aperta ou neutro
- Inventário do `-I` (`git grep -c` por `python3 -I`, `"-I"`, `-I -m`, `-I -c` em todo o repositório, menos o CHANGELOG, na base e no head): 414 → 411 arquivos com ocorrência; os únicos que mudaram são as três skills e `comandos.md` (3 → 1, a linha que resta é a que documenta que `-I` com `tests.<mod>` falha). Todo uso em código segue igual: `bin/forge-testes:543,983,1046,1090`, `bin/forge-fechar:828,1051,1187,1345`, `bin/forge-init:69`, `templates/projeto/.githooks/pre-push:240,327`, `stacks/node-react/seguranca.md:19`, e a regra do subprocesso de teste com ambiente limpo e `-I` em `agents/tech-lead.md:27` (intocado). Nenhum lugar onde o `-I` protege contra código plantado o perdeu: neutro.
- O comando de topo (`python3 -m unittest tests.test_x`, `skills/qa-testing/comandos.md:8`): neutro. O `-I` ali nunca isolou o código da branch: na forma antiga o `discover -s tests` põe `tests/` no `sys.path`, e um módulo plantado em `tests/` com nome da biblioteca padrão é carregado no lugar dela; na nova, a raiz entra no `sys.path` (e os testes do Forge põem a própria pasta). A superfície muda de `tests/` para raiz mais `tests/`, mas a confiança é a mesma: quem roda o teste já executa código da branch, e o arquivo plantado aparece no diff revisado. O que o `-I` de topo ainda dava (ignorar `PYTHONPATH` e o site do usuário) vem do ambiente da própria sessão, não de quem escreve a branch.
- Oráculo EXT-1: a prova de não edição (`skills/qa-testing/SKILL.md:53`) é por commit e blob, não pelo `-I`; um `unittest.py` plantado na raiz para fingir a rodada seria arquivo novo no diff, visível ao review e ao CI. Neutro.
- `tests/test_forge.py:8053-8100`: aperta. O teste passa a exigir a forma uma vez só em `comandos.md`, nenhuma ocorrência de `-I -m unittest discover` em `skills/` e `agents/`, e os ponteiros nas três skills; mantém o teste de que `-I` com `tests.<mod>` não importa. O subprocesso dele roda em diretório temporário próprio com ambiente reduzido a `PATH`; sem entrada externa.
- Fragmento do changelog: neutro.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Sondas de apoio (não provam bloqueante), em diretório temporário com `env -i PATH=...`: módulo `fractions.py` em `tests/` é carregado pela forma antiga com `-I` (1 ocorrência do marcador); o mesmo na raiz é carregado pela forma nova (1) e ignorado pela antiga (0). Confirma que nenhuma das formas isola o código da branch; a troca é neutra.

Verificação: `nice -n 19 python3 -m unittest tests.test_forge.RodarUmModuloComIsolamento` no head 870f0b91: 3 testes, OK. Suíte inteira só no CI: run 45331713345 no head 870f0b91 ainda em fila no momento deste parecer (baterias de passos, pareceres e verificações longas verdes; partes da suíte pendentes); catraca run 45331713202 success. O merge segue preso ao CI verde.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura estática do delta, `git grep` do `-I` base contra head, sondas locais em temporário. Lacuna: o varredor de segredos não está no PATH desta estação (delta só de texto de skill, teste e changelog; o CI cobre a varredura).
