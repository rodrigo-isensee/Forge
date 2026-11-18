---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 89f7ef2f801d5a9d93d973497e7df5caf658027f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.236, item E3.235, `forge-copia --instalar`)

## Achados
- A1 (recomendado) stacks/python/instalar.json:1 · `detecta` só tem `pyproject.toml`, mas a `Detecção` do `pronto.md` da stack lista também `requirements.txt`, `setup.py` e `setup.cfg`: projeto só com `requirements.txt` cai em "nenhuma stack detectada" e a cópia nasce sem dependências.
- A2 (recomendado) stacks/node-react/instalar.json:1 · `pnpm install --frozen-lockfile` sai com erro em projeto sem `pnpm-lock.yaml` (adotado com npm, `pronto.md` linha 13). Sai 1 com a mensagem e a cópia fica; vale dizer isso no `pronto.md` ou no PR.
- A3 (recomendado) docs/adr/0001-nucleo-neutro-e-pacotes-de-stack.md:21 · a ADR lista os arquivos do pacote de stack (`pesados.json` opcional) e não ganhou `instalar.json` (opcional, formato `detecta` e `comandos` em argv). É documentação afetada pela mudança.
- A4 (recomendado) tests/test_forge_copia.py:220 · o teste percorre `stacks/` sem afirmar um mínimo de itens (checklist 11) e confere menos que o código: não exige `detecta` em lista nem argv só de strings. Sugestão: `assertGreaterEqual(len(...), 2)` e a mesma checagem do `instalar()`.
- A5 (recomendado) bin/forge-copia:48 · código e teste somam 152 linhas (45+4 em `bin/forge-copia`, 103 no teste), acima da orientação de 150 (M14). O corpo do PR leva `teto: excedido, 152 linhas, <motivo>`.
- A6 (recomendado) tests/mutantes/v0476-stack-deps.json:87 · a spec tem 10 mutantes; passou de 8, M9 e M10 iriam para `v0476-stack-deps-2.json` (qa-testing, 'Mutantes declarados'). Não é defeito: todos morrem.

## Sondas

## Parecer
Aprovado, sem bloqueante (`R-REVIEW`). Diff `a1674911..89f7ef2f` lido inteiro: `bin/forge-copia`, os dois `instalar.json`, a skill, o teste, a spec de mutantes e o fragmento do changelog.

- **Comportamento:** `instalar()` lê `stacks/*/instalar.json` do próprio plugin (caminho por `realpath(__file__)`, não da cópia), valida o formato (`detecta` em lista, cada comando lista não vazia de strings) e roda cada comando com `subprocess.run(cmd, cwd=copia)`, em argv, sem shell. Spec inválida, comando ausente (`OSError`) e rc diferente de zero saem 1 com mensagem, e a falha interrompe os comandos seguintes. Sem stack detectada, avisa e sai 0. Os dois modos (clone e worktree) só instalam com `--instalar`, e a recusa de pasta vem antes (teste `test_nao_afrouxa_a_recusa_de_pasta`, sai 2 sem criar). Bate com a decisão do dono 4 de 2026-11-17 (cópia com dependências, no pacote da stack, ADR 0001), com as ressalvas A1 e A2.
- **Neutralidade (`R-NEUTRO`, ADR 0001):** `pnpm`, `venv` e `pip` só aparecem em `stacks/`; `bin/forge-copia` e a skill não citam linguagem. O teste usa `sh`, que não é stack.
- **Frases protegidas:** a única linha mudada em `skills/trabalho-em-paralelo/SKILL.md` troca "`forge-copia clone` (padrão)" por "`forge-copia clone --instalar`". Nenhuma das 8 frases de `tests/config.json` para a skill toca essa linha, e `tests.test_jarvis_nucleo` passa.
- **Testes:** `python3 -m unittest tests.test_forge_copia tests.test_sobreposicao_quadro tests.test_jarvis_nucleo tests.test_metricas_texto` deu 132 testes OK. Os testes usam pacote falso em raiz temporária, sem rede, e chamam `python3 -I` com o ambiente da base.
- **Ferramentas:** `python3 -I tests/catraca.py --base origin/develop` deu rc=0. `bin/forge-mutante tests/mutantes/v0476-stack-deps.json` no head 89f7ef2f: M1 a M10 morreram (linhas 52 a 108), um por guarda nova.
- **Segurança:** `pnpm install` e `pip install -e .` rodam scripts do repositório clonado. Isso é próprio de instalar dependências, e o parecer é da segurança (E3.237, `R-SEGURANCA`); não refaço aqui.
- **Suíte:** a suíte inteira fica para o CI do PR.
- Commits no padrão Conventional Commits, em português, um por mudança.
