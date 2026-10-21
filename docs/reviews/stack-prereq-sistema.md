---
tipo: review
contrato: 1
pedido: stack-prereq-sistema
branch: melhoria/stack-prereq-sistema
commit: 399e4f8107be134eb54b2c7aba6f20a977461bc1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: pré-requisitos do sistema na stack node-react (STACK-PREREQ-SISTEMA, M15 opção A)

Escopo: `git diff 0f480c8 399e4f8` (3 arquivos: `stacks/node-react/pronto.md`, `tests/test_stack_prereq_sistema.py`, `changelog.d/stack-prereq-sistema.md`). Revisor em instância distinta do autor (D-ETAPAS-INST). Não toca hooks, catraca, regras com ID nem CI: sem gatilho de `R-SEGURANCA`.

Parecer: **aprovado**.

## Ferramentas (sobre 399e4f8)
- Suíte (`env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests -q`): `Ran 1086 tests in 227.238s`, `OK` (inclui Neutralidade).
- `scripts/validar-plugin.sh`: `✔ Validation passed`.
- `bin/forge-changelog conferir --base 0f480c8`: rc=0.
- Falha antes e passa depois: o teste novo contra o `pronto.md` da base dá `FAILED (failures=4)`; com o `pronto.md` do 399e4f8 sem o `> ` da frase dá `FAILED (failures=1)`; com o 399e4f8 passa.

## Pontos pedidos
- **Instalação é do usuário.** `pronto.md:38` diz "feita pelo usuário", que pede `sudo` e que o agente não usa `sudo` (R-CONFORMIDADE). Conforme a decisão M15 = A.
- **Pré-voo só de leitura.** `pronto.md:39`: `find` + `ldd` + `grep`, nada grava; espera nenhuma linha `not found`; usa `PLAYWRIGHT_BROWSERS_PATH`, que `scripts/configurar-ambiente-local.sh:24` põe no cache, com o padrão do Playwright como reserva. O padrão `*chrome-linux*` cobre `chrome-linux` e `chrome-linux64`.
- **Frase para o usuário.** `pronto.md:41`, em citação, com o comando e o pedido de aviso. O `qa-engineer` já lê o `pronto.md` da stack (`agents/qa-engineer.md:15`), então o texto alcança quem roda o pré-voo.
- **Teste.** `tests/test_stack_prereq_sistema.py` isola a seção pelo título e confere comando, `sudo`, R-CONFORMIDADE, `ldd`, `PLAYWRIGHT_BROWSERS_PATH`, `not found`, `qa-engineer`, "primeira suíte" e a frase em citação; arquivo novo, fora do `tests/test_forge.py`, como o pedido pede.
- **R-NEUTRO.** Os termos de stack ficam em `stacks/node-react/`; o teste e o fragmento citam a stack pelo nome, como os testes de pacote existentes; Neutralidade verde.
- **R-CUSTO.** Pacotes do sistema e um `ldd` local; nada pago.
- **Fragmento.** `### Adicionado` + uma linha `- texto`, formato do `bin/forge-changelog` (`ler_fragmento`).

## Recomendado (não bloqueia, fica para o autor ou um cartão)
- `stacks/node-react/pronto.md:39` · com o cache vazio, o `find` não acha nada, o `ldd` recebe argumento vazio e falha só no stderr (`ldd: ./: not regular file`, rc=1), e o `grep` não imprime linha: a saída é igual à do sucesso. O texto avisa ("o pré-voo vale depois do download"), mas quem lê só a saída pode tomar como verde. Sugestão: dizer "espera: nenhuma linha e o `ldd` sem erro" ou conferir antes que o `find` devolveu um caminho.
- Commits do autor: dois, coerentes (`feat(node-react)` e `docs(changelog)`), Conventional Commits em português; sem ajuste.

## Achados
