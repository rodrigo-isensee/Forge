---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-gerador-unico
commit: aae451ccb8dd8a651cce82ccba20af2a955e2f51
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481, gerador único dos derivados (#946), 1ª rodada

Gatilhos: script que executa código do repositório (`scripts/gerar-derivados.py` roda os geradores da cópia), ambiente do subprocesso.

Lido: `319a968d..aae451cc` inteiro (`scripts/gerar-derivados.py`, `tests/test_gerar_derivados.py`, os dois JSON de mutantes, `skills/engineering-practices/SKILL.md`, `docs/indice-forge.md`, fragmento do changelog) e os dois geradores chamados (`scripts/indice-forge.py`, `scripts/indice-fixtures.py`).

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido, com a evidência:

- Execução de código vinda da cópia: a lista é fechada e literal (`scripts/gerar-derivados.py:20`, `GERADORES`), sem glob, sem argumento do usuário nem leitura de configuração que escolha o que roda; argv é lista, sem shell (`:39-40`). Os geradores são da mesma árvore que o próprio script, então rodá-lo não cruza fronteira de confiança nova: quem roda a cópia já confia no código dela. Nenhum hook, workflow ou script o chama sozinho (só a linha nova da skill, `skills/engineering-practices/SKILL.md:31`, pede ao autor que o rode), então não há caminho de execução automática a partir de branch de terceiro.
- Ambiente limpo: `ambiente()` (`:30-32`) tira todo `GIT_*` e o filho roda com `-I` (`:39`), `stdin` fechado e `cwd` na raiz. Sondas (arquivo de sonda na cópia do revisor, Python 3.12): com `GIT_DIR`, `GIT_WORK_TREE` e `GIT_INDEX_FILE` de outro repositório, `--conferir` segue `em dia`, rc=0 (o `git ls-files` do índice lê a raiz); com `PYTHONPATH` apontando para um `sitecustomize` que deixa sinal, o filho não o carrega (chamada externa com `-I`: sinal ausente).
- `--conferir` não grava: o derivado sujado de propósito sai `desatualizado`, rc=1, e o arquivo fica como estava; os dois geradores tratam `--conferir` antes da escrita (`scripts/indice-fixtures.py:124-127`, `scripts/indice-forge.py:82`). Argumento a mais sai rc=2 sem rodar gerador.
- Sombra de módulo: nenhum `scripts/*.py` tem nome de módulo da biblioteca padrão, então o `scripts/` no `sys.path` da chamada pelo shebang não troca import.
- Skill: as 6 frases encurtadas não mudam regra de segurança nem ID citado.

Notas, sem caminho de ataque (não são achados):
- Pelo shebang (`#!/usr/bin/env python3`, sem `-I`), o processo externo carrega `PYTHONPATH` do ambiente (sonda: o `sitecustomize` deixou sinal no processo externo, nunca no filho). Quem controla o ambiente do autor já executa código nele; é o mesmo padrão dos outros scripts de `scripts/`.
- Em `--conferir`, um gerador que quebre com exceção também sai rc=1 e aparece como `desatualizado` (`:52-53`), não como `gerador vermelho`. Falha fechada (rc final 1); é texto de diagnóstico, do `tech-lead` se quiser cartão.

CI do head aae451cc (`gh pr checks 946`): suíte (5 partes), instalação, bateria de passos, longas, python 3.14, teto de pulados, árvore provada e catraca verdes; `bateria` e `bateria (pareceres)` vermelhas por parecer ainda ausente, fora do código. Local: `tests.test_gerar_derivados`, 10 testes OK.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura e sondas locais; `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` ausentes no PATH (lacuna do ambiente; o diff não traz dependência nem workflow).
