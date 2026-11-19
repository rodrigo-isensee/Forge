---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 9a20739e0d4ff607033690eaa238e6c0342e6d74
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.27, revalidação)

Volta por delta. Rodada anterior: `commit 9b075525` (E3.22), no git. Delta lido (`forge-check parecer delta`, `9b075525..9a20739e`): no domínio, `hooks/parecer.py` (`EXPANSAO_QUE_ATRIBUI`, `mexidas_por_expansao` e o ambiente inicial em `principal`, commit 415eaa82, A5 do review), `tests/test_hooks_parecer_matriz.py` (D4 por expansão, S28 e S29, legítimos novos) e a linha D4 de `docs/hooks.md`. Fora do domínio, não relido: o fragmento do changelog e `tests/mutantes/v0478-guardas-parecer-10.json`.

Gatilhos: hook de controle (`hooks/parecer.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A9 (bloqueante) hooks/parecer.py:1140 · D4 por expansão lê o texto cru: com `\`+quebra dentro da chave, `set -a; : ${GH_\<nl>REPO:=dono/forge}; gh pr ready feature/x` dá 0 e o bash exporta GH_REPO (S30). A correção do A5 não cobre a forma que o shell lê.
- A10 (bloqueante) hooks/parecer.py:127 · D4 sem a atribuição aritmética: `: "$((HOME=0))"`, `: $[HOME=0]`, `: ${A[HOME=0]}`, `: ${PWD:HOME=0:0}` antes do gh dão 0; o bash põe HOME=0 e o git lê `0/.gitconfig` da cópia alheia (S31 a S34). Mesma família do A5, dimensão nova da matriz.

## Sondas
- S30 · `set -a; : ${GH_\` + quebra de linha + `REPO:=dono/forge}; gh pr ready feature/x` · espera: 2 · obtido: 0
- S31 · `: "$((HOME=0))"; gh pr ready feature/x` · espera: 2 · obtido: 0
- S32 · `: $[HOME=0]; gh pr ready feature/x` · espera: 2 · obtido: 0
- S33 · `: ${A[HOME=0]}; gh pr ready feature/x` · espera: 2 · obtido: 0
- S34 · `: ${PWD:HOME=0:0}; gh pr ready feature/x` · espera: 2 · obtido: 0

## Detalhe dos achados
**A9 (média, bloqueante).** Evidência: `hooks/parecer.py:1140` passa `comando` cru a `mexidas_por_expansao` (`hooks/parecer.py:651`); o `\`+quebra de linha some na leitura do bash, também dentro de `${…}`, e a regex de `hooks/parecer.py:127` não casa `${GH_\<nl>REPO:=…}`. Conferido no bash: depois de `set -a; : ${GH_\<nl>REPO:=dono/forge}`, o ambiente traz `GH_REPO=dono/forge`, e o gh age no repositório do Forge a partir da cópia alheia. Caminho de ataque: o do A5 (agente numa cópia alheia sem `-R`, evasão deliberada ou cópia de trecho), com uma quebra a mais. Correção mínima: somar `mexidas_por_expansao` sobre cada texto de `textos_da_linha(comando)` (`hooks/parecer.py:513`, que já traz as formas que o shell lê), não só sobre `comando`; S30 no gerador (posição nova em `POSICOES_DA_EXPANSAO`). Esforço P. Dono: tech-lead.

**A10 (média, bloqueante).** Evidência: `EXPANSAO_QUE_ATRIBUI` (`hooks/parecer.py:127`) só cobre `${N:=v}` e `${N=v}`; a aritmética do bash também dá valor, e `HOME` já vem exportado (sem `set -a`). O `$((HOME=0))` sem aspas recusa (2), mas pelo caminho da dúvida da leitura, não pela D4; entre aspas, e nas outras três formas, dá 0. Conferido: `: "$((HOME=0))"; git config --get remote.origin.gh-resolved` numa cópia com `0/.gitconfig` devolve `dono/forge`. O valor é só numérico, mas basta para `HOME`, `XDG_CONFIG_HOME`, `GH_CONFIG_DIR`, `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `CDPATH` (pasta `0` relativa, gravada antes noutra chamada). Contextos aritméticos que atribuem, lista inteira para cobrir: `$((…))`, `$[…]`, `((…))`, `for ((…))`, `let`, subscrito de vetor indexado (`${A[…]}` e `A[…]=`), deslocamento e tamanho (`${N:…:…}`) e os operandos de `[[ … -eq|-ne|-lt|-le|-gt|-ge … ]]`; operadores: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `^=`, `|=`, `++` e `--` (antes ou depois do nome). Correção mínima, falha fechada: em todo texto de `textos_da_linha`, nome de `SENSIVEIS` ou `GIT_*` seguido de um desses operadores (não `==`, `!=`, `<=`, `>=`), ou precedido de `++` ou `--`, conta como mexido onde quer que esteja (recusa a mais, como a D4 já declara para a expansão); a forma nova na linha D4 de `docs/hooks.md` e S31 a S34 no gerador. Esforço P. Dono: tech-lead.

## Estado dos achados anteriores
- **A5 (review), S28 e S29:** as formas do gerador recusam (2), conferidas também fora dele: `${GH_REPO:=…}` no corpo de heredoc e em duas linhas físicas dão 2. Incompleto pelo A9 e pelo A10.
- **A8 (D7, `PATH`):** decidido pelo dono (opção b, limite do hook coberto pela A3 da E29); não reaberto aqui.
- **A1 a A7:** fechados antes; sem delta que os toque.
- Corpus de legítimos, todos 0: `gh pr ready feature/x`, `: ${PAGER:=less};`, `set -a; : "${GH_REPO:-dono/forge}";` e os do gerador.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Cenário das sondas: o do gerador (`tests/test_hooks_parecer_matriz.py`, base `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia.json`), com o lançador da suíte, por um script local fora do repositório; o efeito no bash e no git conferido em pasta temporária. Teste rodado: `python3 -m unittest tests.test_hooks_parecer_matriz` (OK, 6 testes, 17 s). A suíte inteira roda no CI; o brief não cita CI deste head. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
