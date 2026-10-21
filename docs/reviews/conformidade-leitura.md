---
tipo: review
contrato: 1
pedido: conformidade-leitura
branch: melhoria/conformidade-leitura
commit: f6cd7ae74ab4389fedbb4d440d3673a5e9baed1c
parecer: reprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-21
---
# Review do CONFORMIDADE-LEITURA (E1.2)

Escopo lido: `git diff f911dfa0b2ebd9692d45c374f9ff4bab8523ed6b f6cd7ae74ab4389fedbb4d440d3673a5e9baed1c` (`hooks/conformidade.py`, 13 fixtures `tests/hooks/conformidade/leitura-*.json`, `changelog.d/conformidade-leitura.md`), a seção M1 da proposta e a decisão técnica do recorte de leitores no Histórico do pedido. A revisão de segurança é da E1.3 (`docs/security/conformidade-leitura.md`) e não se refaz aqui.

## Achados
- A1 (bloqueante) hooks/conformidade.py:179 · `so_leitura` confia em `comandos()`, cujo shlex trata `#` colado à palavra como comentário; o bash não. `grep sugerir f#;forge sugerir --fila` passa (rc 0, base f911dfa: rc 2). Recusar `#` na linha e fixture de recusa.

## O que confere
- Faz o que o E1 e o E2 pedem: a exceção vale só quando todo segmento é leitor sem execução ou `git log|show|diff`, sem `$`, crase, quebra de linha, substituição, subshell nem redirecionamento de saída; fora disso, a F6 segue como estava. Nenhuma fixture de recusa existente saiu (o diff só adiciona).
- O recorte `LEITORES_SEM_EXEC` (sem `source`, `.`, `less`, `more`, `bat`, `xxd`) é mais restrito que o decidido, conforme a decisão técnica de 2026-10-21 00:43. As opções são lista branca (curtas por letra, longas pelo nome exato); `--pre`, `--filter`, `--pre-glob`, `-z`, `--output`, `--ext-diff`, `git -c` e `git --no-pager` recusam, o que cobre o GREP-OPCOES-EXEC pelo lado da exceção.
- Sondas (cópia em `$TMPDIR`, harness `tests/test_hooks.py`, sem trocar o HEAD da worktree): `grep -n 'forge sugerir' README.md` e `grep -rn forge docs/*.md` → rc 0; `forge sugerir --fila` → rc 2; `cat <(forge sugerir --fila)`, `grep x f && forge sugerir`, `grep x f | sh`, `grep x f |& forge sugerir`, `{ grep sugerir f; }` → `so_leitura` False. A falha é só a do A1: `grep -n x README.md#;forge sugerir --fila` e `cat a#&&forge sugerir --fila` também passam com rc 0 em f6cd7ae e dão rc 2 em f911dfa.
- Código legível, funções pequenas e docstrings que dizem o contrato; changelog em fragmento; commit em Conventional Commits.

## Recomendações (não bloqueiam)
- R1: a causa do A1 é anterior a esta entrega e mais larga: em f911dfa, `cat a#&&git push origin main` passa no hook (rc 0), contra rc 2 de `git push origin main` (R-MAIN). Vira cartão para o `security-engineer` (parser `fichas`/`comandos` em `hooks/_comum.py`); a correção do A1 aqui não depende dele.
- R2: palavra com glob no início (`rg sugerir *`) pode expandir para um arquivo chamado `--pre=...`. O vetor já existe sem a exceção (`rg x *`), então fica para o GREP-OPCOES-EXEC; se a correção do A1 quiser fechar junto, basta recusar na exceção a palavra que começa com `*`, `?` ou `[`.
- R3: `2>/dev/null` e `git --no-pager log` saem da exceção (conservador, aceito). Se a métrica do M1 mostrar recusas por eles, dá para tratar `2>/dev/null` como destino nulo.
- R4: a docstring de `sugerir_na_linha` (hooks/conformidade.py:784) tem uma linha bem mais longa que as vizinhas; quebrar como o resto.

## Ferramentas
A suíte (`python3 -m unittest discover -s tests -v`) e o `scripts/validar-plugin.sh` são decididos por ferramenta e rodam no pre-push deste parecer; não foram refeitos à mão. O autor relatou 1194 OK em f6cd7ae (Histórico do pedido).
