---
tipo: review
contrato: 1
pedido: conformidade-leitura
branch: melhoria/conformidade-leitura
commit: 2e1e7129d7494912f5de2dba382dae15a5d64c4b
parecer: aprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-21
---
# Review do CONFORMIDADE-LEITURA (E1.2)

Escopo lido: `git diff f911dfa0b2ebd9692d45c374f9ff4bab8523ed6b f6cd7ae74ab4389fedbb4d440d3673a5e9baed1c` (`hooks/conformidade.py`, 13 fixtures `tests/hooks/conformidade/leitura-*.json`, `changelog.d/conformidade-leitura.md`), a seção M1 da proposta e a decisão técnica do recorte de leitores no Histórico do pedido. A revisão de segurança é da E1.3 (`docs/security/conformidade-leitura.md`) e não se refaz aqui.

## Achados

## Volta 2
Delta lido: `git diff 95a7321 2e1e712` (só `hooks/conformidade.py`, `so_leitura`) e a resolução do merge 95a7321 nesse arquivo (`git diff fa75b67 95a7321 -- hooks/conformidade.py`). O resto da branch ficou como "já lido" nas voltas 0 e 1; os demais arquivos do merge vêm da develop (#265 a #269) e não são desta entrega.

- Merge: em `hooks/` a diferença entre a develop (fa75b67) e 95a7321 é só o que a entrega já trazia (constantes, `opcoes_sem_exec`, `so_leitura`, a chamada em `sugerir_na_linha`). Nada da #269 foi revertido nem afrouxado.
- 95a7321 sozinho quebra: `comandos` saiu do import com a #269 e `so_leitura` dava NameError (o hook caía fechado, sem liberar nada). 2e1e712 corrige trocando por `leituras()`, a porta única da ADR 0013.
- Equivalência: a recusa de `$`, crase, `#` e quebra de linha segue antes; sem `#`, `leituras()` devolve só a leitura fiel, então o comportamento é o da volta 1. A troca ainda recusa a linha ilegível e a de mais de uma leitura, o que só estreita.
- Nada além da M1 é liberado: o diff do delta não toca constantes, opções nem `sugerir_na_linha`.
- Sondas (cópia de 2e1e712 em `$TMPDIR`): `python3 -m unittest tests.test_hooks` 41 testes OK; `so_leitura` True para `grep -n forge README.md`, `grep -n 'forge sugerir' README.md`, `git log --oneline -- forge`; False para `grep sugerir f#;forge sugerir --fila`, `grep x f && forge sugerir`, `grep x f | sh`, `cat <(forge sugerir)`, aspa sem par, `grep --pre=sh x f`, `xargs forge sugerir`, `grep x f; forge sugerir --fila`, `grep x f > o`.
- Sem achado novo.

## Volta 1
Delta lido (`forge-check delta --parecer` sobre o parecer anterior, intervalo f6cd7ae..590579d; o código muda só em a0f766f, os demais commits são pareceres): `hooks/conformidade.py`:176 e :179 e as 3 fixtures `leitura-cerquilha-colada-*-bloqueia.json`. O resto da branch ficou como "já lido" na rodada anterior.

- A1 (volta 0) resolvido: `so_leitura` recusa qualquer `#` na linha antes do `comandos()`, e a docstring diz por quê. Recusar a linha toda é conservador: quem lê com `#` só perde a exceção e volta à F6 de antes, sem afrouxar nada.
- Fixtures cobrem as três formas do A1 (`f#;forge`, `a#&&forge`, `f#; forge`), todas com rc 2 e o stderr da F6.
- Sondas (cópia em `$TMPDIR` de a0f766f): `python3 -m unittest tests.test_hooks` 34 testes OK; `so_leitura` dá True para `grep -n forge README.md` e False para `grep sugerir f#;forge sugerir --fila`, `grep "#" f`, `cat a\#;forge sugerir` e `grep x f;# forge sugerir`.
- Achado A1 encerrado; sem achado novo. As recomendações R1 a R3 seguem como estavam.

## O que confere
- Faz o que o E1 e o E2 pedem: a exceção vale só quando todo segmento é leitor sem execução ou `git log|show|diff`, sem `$`, crase, quebra de linha, substituição, subshell nem redirecionamento de saída; fora disso, a F6 segue como estava. Nenhuma fixture de recusa existente saiu (o diff só adiciona).
- O recorte `LEITORES_SEM_EXEC` (sem `source`, `.`, `less`, `more`, `bat`, `xxd`) é mais restrito que o decidido, conforme a decisão técnica de 2026-10-21 00:43. As opções são lista branca (curtas por letra, longas pelo nome exato); `--pre`, `--filter`, `--pre-glob`, `-z`, `--output`, `--ext-diff`, `git -c` e `git --no-pager` recusam, o que cobre o GREP-OPCOES-EXEC pelo lado da exceção.
- Sondas (cópia em `$TMPDIR`, harness `tests/test_hooks.py`, sem trocar o HEAD da worktree): `grep -n 'forge sugerir' README.md` e `grep -rn forge docs/*.md` → rc 0; `forge sugerir --fila` → rc 2; `cat <(forge sugerir --fila)`, `grep x f && forge sugerir`, `grep x f | sh`, `grep x f |& forge sugerir`, `{ grep sugerir f; }` → `so_leitura` False. A falha é só a do A1: `grep -n x README.md#;forge sugerir --fila` e `cat a#&&forge sugerir --fila` também passam com rc 0 em f6cd7ae e dão rc 2 em f911dfa.
- Código legível, funções pequenas e docstrings que dizem o contrato; changelog em fragmento; commit em Conventional Commits.

## Recomendações (não bloqueiam)
- R1: a causa do A1 é anterior a esta entrega e mais larga: em f911dfa, `cat a#&&git push origin main` passa no hook (rc 0), contra rc 2 de `git push origin main` (R-MAIN). Vira cartão para o `security-engineer` (parser `fichas`/`comandos` em `hooks/_comum.py`); a correção do A1 aqui não depende dele.
- R2: palavra com glob no início (`rg sugerir *`) pode expandir para um arquivo chamado `--pre=...`. O vetor já existe sem a exceção (`rg x *`), então fica para o GREP-OPCOES-EXEC; se a correção do A1 quiser fechar junto, basta recusar na exceção a palavra que começa com `*`, `?` ou `[`.
- R3: `2>/dev/null` e `git --no-pager log` saem da exceção (conservador, aceito). Se a métrica do M1 mostrar recusas por eles, dá para tratar `2>/dev/null` como destino nulo.
- R4: a docstring de `sugerir_na_linha` (hooks/conformidade.py:784) tem uma linha bem mais longa que as vizinhas; quebrar como o resto. A primeira linha da docstring de `so_leitura` (hooks/conformidade.py:176, 175 caracteres) ficou no mesmo caso na volta 1, e a segunda linha dela (hooks/conformidade.py:177) passou a ser a mais longa na volta 2.
- R5: o merge 95a7321 ficou num commit que não passa na suíte (NameError em `so_leitura`); numa próxima, resolva o merge e a quebra que ele traz no mesmo commit, para cada commit seguir verde.

## Ferramentas
A suíte (`python3 -m unittest discover -s tests -v`) e o `scripts/validar-plugin.sh` são decididos por ferramenta e rodam no pre-push deste parecer; não foram refeitos à mão. O autor relatou 1194 OK em f6cd7ae (Histórico do pedido).
