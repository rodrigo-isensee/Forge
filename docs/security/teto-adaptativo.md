---
tipo: revisao-seguranca
contrato: 1
pedido: teto-adaptativo
branch: melhoria/teto-adaptativo
commit: 54852d4e5bde991de5a2691dc4fa979d9ce01d4e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: teto-adaptativo (volta 2, revalidação por delta)

Escopo: `git diff da15a888..54852d4e` (`hooks/agentes.py`, `bin/forge-check`, `docs/hooks.md`, `docs/regras/R-TETO.md`, testes). Revisão estática; `tests.test_hooks` rodou verde (24 testes). Substitui o parecer da volta 1 (119bc506).

## Gatilhos
Hook de controle (`hooks/agentes.py`, ADR 0003) e regra de conformidade (R-TETO, R-WIP); `forge-check kanban` é verificador de regra.

## Achados

## Detalhe dos achados
Conferências pedidas (todas cumpridas em 54852d4e):
- Sem leitura de /proc o teto cai em 3 (falha segura): `hooks/agentes.py:67-73` devolve `min(3, nproc)` se nproc é conhecido, senão 3; nunca acima de 3. Sem medida, `carga_alta` não bloqueia (`:62-63`), mas o teto segue valendo.
- `teto_agentes` e `teto_maximo` continuam sobrepondo: `calcular_teto` (`:76-92`) aplica o fixo e depois `teto_maximo` aos dois (agora limita também o fixo, mais restritivo, nunca mais frouxo). O `forge-check kanban` (`bin/forge-check:244`) chama a mesma função, sem a lógica duplicada que divergia. A trava de carga vale antes e não é desligada por eles (`agentes.py:113`).
- FORGE_NPROC e FORGE_PROC (R1 da volta 1, corrigido): `agentes.py:110-112` registra no erros.log cada uso (`registrar_escape`, `_comum.py:693`, nunca bloqueia), documentado em `docs/hooks.md`. São variáveis do ambiente do processo do hook, herdado do dono; um agente pelo Bash não as altera. Não abrem caminho para desligar o teto: FORGE_NPROC inválido ou 0 cai em None (teto 3); negativo bloqueia tudo (falha fechada); FORGE_PROC inexistente zera a medida (teto 3, trava de carga inerte, igual ao escape FORGE_CARGA_LIVRE já aceito, agora com registro). O `forge-check kanban` não registra, mas só lê o quadro.
- nproc por afinidade (R2 corrigido): `agentes.py:30-39` usa `os.sched_getaffinity(0)` com queda para `cpu_count()`; `OSError` tratado.
- Tarefas pesadas uma por vez: `hooks/pesado.py` fora do delta e intacto; `R-TETO.md` mantém o texto.
- Fator de coluna não remove o 1 cartão por agente: o delta não toca `fator_de_coluna` nem `instancias_do_agente`; a verificação da volta 1 segue valendo (só limites `total` escalam; tipo `agente` mantém 1).
- Erro interno do hook: registra e libera (ADR 0003), inalterado.

Recomendações anteriores: R2 resolvida, R1 resolvida. R3 (load de 1 min atrasa; rajada pode chegar a nproc) e R4 (resultado do kanban depende da máquina, decisão do dono) seguem informativas, sem caminho de ataque realista.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e `unittest`; gitleaks, osv-scanner e semgrep não necessários (sem dependência nem segredo novo no delta) nem executados.
