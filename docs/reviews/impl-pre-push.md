---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c4
commit: 79880e375470b3efd45c68b8acab815afa3912d7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c4 (TRAVA-SANDBOX, trava comum)

Diff lido na primeira rodada: `234dbe0..aff0ec2` (2 commits: `a515d73` hook e testes, `aff0ec2` fragmento).

## Revalidação no head 79880e3 (merge da develop 08da90c, delta lido)
`forge-check delta --parecer` (intervalo `ddb7768..79880e3`) lista o que a develop trouxe (C1, C2, C5, C-14, `bin/`, docs, versão). Li só a resolução do merge em `.githooks/pre-push` e `tests/test_pre_push_trava.py` (`git diff 23716c4 79880e3` e `git show --cc 79880e3`):
- O patch próprio da branch não mudou: as linhas `+`/`-` de `git diff 234dbe0 ddb7768` e de `git diff 08da90c 79880e3` em `.githooks/`, `tests/` e `bin/` são idênticas (`diff` rc 0).
- Hook: as funções da develop (`modo_sem_escrita_alheia`, `texto_da_trava`, `status_erro`, campo `ns` da trava) entram sem tocar o candidato único da pasta comum; a conferência de modo do C1 passa a valer também para `~/.forge-contrib/forge-<uid>` (criada com 700), o que reforça o C-10.
- Teste: o conflito juntou o teste C-14 da develop (`:578`) e os do C4 (`:595` em diante); os da develop usam `HOME` temporário sem `.forge-contrib` e seguem na trava de `XDG_RUNTIME_DIR`. Resolução correta.
- O A1 da rodada anterior fica resolvido: o C-14 chegou pela develop e está neste head.
- M14 no head (`git diff --numstat --no-renames origin/develop...HEAD`, código e teste): 20 + 122 + 4 x 2 = 150; no teto, um comportamento. Cumpre.
- Já lido, sem mudança: o restante do hook e dos testes do C4 e o fragmento; o resto do delta é código da develop, revisado nos PRs de origem.

## Revalidação no head ddb7768 (delta lido)
`forge-check delta --parecer` (intervalo `aff0ec2..ddb7768`): só `tests/test_pre_push_trava.py` (+5 -1, linhas 535-538 e 540), o subcaso "comum link pendente" do C-9 (A1 do QA). Li só isso: o subcaso troca a pasta comum por link para destino inexistente e entra no mesmo laço de subtestes; correto. O hook não mudou. Já lido, sem mudança: hook, demais testes e fragmento (parecer anterior); o resto do delta são pareceres de segurança e QA, fora do código.
- M14 no head (`git diff --numstat --no-renames 234dbe0 ddb7768`): hook 20, `tests/test_pre_push_trava.py` 122, 2 em cada um dos outros quatro módulos; total 150, no teto de 150 ("até 150"). Um comportamento só; cumpre. Sem folga: qualquer linha nova nesta branch estoura o teto.
- Nota de estilo, não achado: a linha 540 do teste ficou comprida; vira recomendação só se o formatador do projeto a barrar no CI.

## O que entrega
Item E3 do pedido, C4 do desenho com os controles C-9 a C-13 e C-15 do modelo (`docs/security/ameacas/pre-push.md`), na opção Q-S1 = B:
- `trava_arquivo` (`.githooks/pre-push:14-48`): com `$HOME/.forge-contrib` presente (`-e` ou `-L`), o único candidato é ela, sem recuo (C-9); ausente ou `HOME` vazio, a ordem de antes. A subpasta passa pelas mesmas conferências (C-10; o modo `/022` é do C1, em outra branch).
- Provas `.verde` e `.dirigida` ficam na pasta de cada lado, pelo segundo argumento `legado` (`:179`, C-12); falha nessa resolução zera as provas e `anotar` passa a ignorar caminho vazio, então só se perde o atalho: a suíte roda.
- `HOME` temporário nos cinco módulos que executam o hook e o teste estrutural `TodoTesteDoHookUsaHomeTemporario` (C-13), com mínimo de 5 módulos afirmado (checklist 11). Conferi: os 5 módulos que casam o padrão são exatamente os que executam o hook; `test_pre_push_shellcheck.py` só lê o arquivo.
- Testes T-C4a, b, c, e, g: mesma trava dentro e fora do sandbox; pasta comum recusada sem recuo (link, arquivo, sem escrita) no push e no `--suite`, sem nada criado em `XDG_RUNTIME_DIR` nem `TMPDIR`; `--status` sem subpasta não cria nada (C-11); prova de um lado não dispensa a suíte no outro.
- Fragmento com o aviso de transição das worktrees (C-15).

## M14 (decisão M14, agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 aff0ec2`): `.githooks/pre-push` 20, `tests/test_pre_push_trava.py` 118, e 2 em cada um de `test_pre_push_afetados.py`, `test_pre_push_parecer.py`, `test_pre_push_parecer_curto.py` e `test_suite_paralela.py`; total 146, abaixo de 150 (no head ddb7768 são 150, ver a revalidação). O fragmento fica fora.
- Um comportamento só (onde a trava e a fila moram); o `HOME` temporário é a condição de teste desse comportamento, não outro. Sem exceção de teto (que não valeria em `.githooks/`). Cumpre.

## Regras de ferramenta
- Suíte: branch no `origin` com o head revisado; o pre-push rodou a suíte inteira no envio do autor (diff em `.githooks/`). O CI do PR repete.
- shellcheck: ausente nesta máquina; fica para o CI. Pendência, não review manual.
- Mutação: sem `tests/mutantes/impl-pre-push*.json`. Pendência do autor (V2): a condição nova de `:18` e o guarda de `anotar` pedem spec.

## Leitura
- Falha fechada conferida: pasta comum como arquivo, sem escrita ou com subpasta link ou arquivo cai no fim do laço ou na recusa, rc 1, sem tentar outro candidato.
- `--status` com a recusa ainda sai com 1 nesta branch; o 2 é do C2 (outra branch). O teste aceita 1 ou 2 e afirma que não diz "nenhuma suíte" (`tests/test_pre_push_trava.py:551`), sem afrouxar.
- R-NEUTRO, R-CUSTO e invariantes preservados. Gatilho R-SEGURANCA (pasta e permissões da trava, fronteira do sandbox, ADR 0009): o parecer de segurança é do `security-engineer` (E1.3), não refeito aqui.

## Achados
- A1 (recomendado) .githooks/pre-push:59 · Resolvido no head 79880e3: o C-14 (texto da trava limitado e imprimível) chegou pela develop em `texto_da_trava`; a ordem de integração pedida já está cumprida.
- A2 (recomendado) .githooks/pre-push:179 · Se a pasta das provas for recusada, `trava_arquivo criar legado` imprime "recusada. Apague-a" e o push segue; a mensagem sugere falha. Calar o stderr nessa chamada ou dizer que só a prova foi ignorada.
- A3 (recomendado) .githooks/pre-push:23 · Spec de mutação ausente para a condição da pasta comum e o guarda novo de `anotar`; pendência V2 do autor.
- A4 (recomendado) tests/test_pre_push_trava.py:665 · Com o C2 já na develop, `assertIn(codigo, (1, 2))` pode virar `assertEqual(codigo, 2)`; mudar aqui estoura o teto de 150, então fica para PR próprio.

## Parecer
Aprovado, mantido no head 79880e3 (o merge da develop não mudou o patch da branch). Entrega o C4 do E3 com os controles do modelo e cumpre a M14 (150 linhas no head, um comportamento). A1 está resolvido pela develop; A2, A3 e A4 não devolvem.
