---
tipo: review
contrato: 1
pedido: fechar-master
branch: melhoria/fechar-master
commit: 14a6b0cd8595be38b05927a5083a11b4a9b76776
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: fechar-master

Base `139a3b451a1c367ed7764257486c0a0f39c73e8b`, head `14a6b0cd8595be38b05927a5083a11b4a9b76776` (2 commits: `42fbfe2` teste vermelho, `14a6b0c` recusa; 3 arquivos: `bin/forge-fechar`, `tests/test_fechar_longas.py`, `changelog.d/fechar-master.md`).

## Achados
- A1 (recomendado) bin/forge-fechar:57 · o comentário diz "a primeira palavra entre crases na linha que cita integração", mas a linha 61 pega o primeiro trecho entre crases de todas as linhas que citam integração; alinhar o comentário ao código ou parar na primeira linha
- A2 (recomendado) bin/forge-fechar:61 · falha aberta: "Ninguém envia para `main`; integração em `trunk`" lê `main`, e uma linha anterior com outro trecho entre crases o lê no lugar da branch; ancorar em "Branch de integração: `x`" e fixar o formato no modelo de CLAUDE.md (cartão)
- A3 (recomendado) bin/forge-fechar:59 · lê só `CLAUDE.md` da raiz; o Forge mantém o seu em `.claude/CLAUDE.md`, e fora do Forge a guarda R-CONTRIB (linha 139) já para antes de qualquer ação, então hoje o ramo do CLAUDE.md não protege nada além da lista fixa; registrar isso no comentário ou ler também `.claude/CLAUDE.md`

## O que li
- Ordem: a lista fixa (`main|master|develop|homolog`, linha 56) e a leitura do `CLAUDE.md` (linhas 58 a 63) vêm logo depois do parse dos argumentos. Antes dela só roda `git rev-parse --show-toplevel`, que só lê. A recusa vem antes do `check-ref-format`, da base, do log, da guarda do Forge, do `forge-check`, de qualquer `fetch`/`gh` e do passo 7 (`--limpar`). Entre as linhas 80 e 139 não há ação sobre branch.
- Leitura do `CLAUDE.md` sem a linha: `grep` sem resultado devolve vazio (o `|| true` cobre o `pipefail`) e só vale a lista fixa, coberto por `test_sem_a_linha_no_claude_md_branch_de_trabalho_segue_valida`. Quando a linha cita outra coisa, o resultado é um falso negativo (A2), nunca a recusa de uma branch de trabalho legítima: a recusa só dispara se `--ref` for exatamente igual ao trecho lido. Sondas em `$TMPDIR/tech-lead-fecharmaster/`: `c1` (formato canônico) dá `trunk`; `c2` dá `main`; `c3` dá `forge-check sobreposicao`; `c4` (maiúsculas) e `c5` (sem acento) dão `trunk`; com `LC_ALL=C` o resultado é o mesmo. A falha é aberta, mas o risco real é baixo: no Forge a integração é a `develop`, que já está na lista fixa, e em projeto a guarda R-CONTRIB para antes (A3). Por isso os três achados ficam como recomendados.
- Teste: `test_branches_longas_fixas_sao_recusadas_com_e_sem_limpar` reproduz a sonda do QA da LIMPEZA-REGRA (A1/CT-05). Ele cria a `master` local e remota, roda `--ref master --limpar` e confere que `git branch -a` não mudou e que não houve chamada a `forge-check` nem a `gh`. Sem a recusa, o `--limpar` chamaria o `gh` para provar o merge e o teste falharia, o que bate com o commit vermelho `42fbfe2`. A branch de integração é coberta com e sem `--limpar`, e a branch de trabalho segue válida com a linha presente.
- Changelog: `### Corrigido` diz o mesmo que o código (recusa `master` e a branch de integração do CLAUDE.md, além das três, antes de qualquer ação). A precisão do "do CLAUDE.md do projeto" depende de A2 e A3.
- Regras: `R-VERIFY` e `R-FLUXO` citadas na mensagem. Nada de `--force` nem `--no-verify`. `R-NEUTRO` respeitado (`trunk` é um nome genérico). `R-CUSTO` sem impacto.

## Ferramentas (citadas, não refeitas à mão)
- `python3 -m unittest tests.test_fechar_longas tests.test_fechar -v`: `Ran 84 tests in 30.850s` / `OK`.
- `shellcheck -S warning bin/forge-fechar`: 1 aviso (SC2034 `comuns`, linha 457), o mesmo que já existe na base `139a3b4`; nada novo. O `bin/forge-fechar` não está na lista de shellcheck do CI (`.github/workflows/ci.yml:159`); fica como pendência fora deste diff.
- Segurança e QA: pareceres próprios (E2.1, E3.1), não refeitos aqui.

## Parecer
Aprovado. A recusa de `master` fecha o A1 do QA da LIMPEZA-REGRA, vem antes de qualquer ação e tem teste vermelho e depois verde com a sonda. A leitura da branch de integração resolve o formato canônico e falha aberta nos outros (A1 a A3, recomendados, para um cartão de formato da linha no modelo de CLAUDE.md).
