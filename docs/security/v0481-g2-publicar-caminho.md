---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-publicar-caminho
commit: 0cdf17c362c8ecb59196d5234a7db013ea334e71
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E21.9 (#916, G2 publicar confere caminho, 1ª rodada completa)

## Gatilhos
Gatilhos: controle do Forge (`recusa_do_publicar` em `bin/forge-check`, o portão `forge-check parecer publicar` que lê o registro de autoria do hook `conformidade`)

Sem a linha `ci:` verde, porque a suíte não chegou ao fim em nenhum head com esta árvore de código. No `0cdf17c3` (run 45855084791), as 10 partes da suíte e o teto de pulados foram cancelados pelo push do parecer de QA. No `b9461e5d` (run 45855533690, que só acrescenta `docs/qa/`), foram cancelados pelo push do review (`c8180f0d`). Nos dois runs ficaram verdes a `árvore já provada na develop`, a `bateria (passos)`, a `bateria (verificações longas)` e a instalação (python 3.14). Li a causa de cada falha no log. A `bateria (pareceres)` falha por R-REVIEW ("PR toca bin/forge-check... sem parecer aprovado de review"), que é espera. A `bateria (python 3.14)` e a `bateria` falham só porque "partes: cancelled; pulados: cancelled". A `catraca` (run 45855084877) falha por R-CONFORMIDADE ("mudança em bin/forge-check"), à espera do rótulo do dono. Vale a suíte do head que vier depois deste parecer, com a mesma árvore de código, e quem mescla a confere.

## Escopo lido
`git diff 3c833f3f..0cdf17c3` (merge-base com a develop): `bin/forge-check:3883-3911` (a constante `PARECER_A_PUBLICAR` e `recusa_do_publicar`), `tests/test_conformidade_pareceres.py` (3 testes novos), `tests/test_forge_pareceres.py:253`, `tests/mutantes/v0481-g2-publicar-caminho.json` (M38 a M42), `tests/mutantes/v0481-g2-1-publicar-3.json` (M17 e M18) e o fragmento do changelog. Também li o lado que grava: `autoria`, `raiz_do_parecer` e `PARECER_A_PUBLICAR` em `hooks/conformidade.py:4049-4087`, `autorias` (`bin/forge-check:1428`) e o `--raiz` padrão (`bin/forge-check:11161`, 11493).

## Mitigações do modelo de ameaças
- **M9.1** (T9 em `docs/security/ameacas/g2-parecer-status.md`): fica mais forte. A autoria vale só se o último registro de `autoria.jsonl` com `caminho` igual ao do arquivo publicado (relativo à raiz, como o hook grava em `hooks/conformidade.py:4082`) tiver o sha256 do texto e o papel do tipo (`bin/forge-check:3908-3910`). Provas: `test_s1_texto_de_docs_reviews_publicado_de_fora_do_projeto`, `test_s1_texto_de_docs_reviews_copiado_para_o_parecer_a_publicar` e `test_s2_veredito_superado_nao_volta_a_publicar`. Os três falham com o `bin/forge-check` da base (3 FAIL) e passam no head.
- **M9.2:** sem mudança. A regex do portão agora é a do hook (`[A-Za-z0-9][A-Za-z0-9._-]*/[a-z-]+\.md`, com `fullmatch` sobre o relativo), e os dois lados conferem a mesma forma.

## Detalhe
Não há achado no diff. O cartão que abri no parecer do #914 (`docs/security/v0481-g2-autoria.md`, "Cartão (fora do diff...)") está cumprido como escrevi: o caminho igual ao `rel`, o último registro daquele caminho e as sondas (1) e (2) viraram testes de recusa.

**Sondas do #914, agora.** Rodei as sondas com o `gh` falso do teste e o hook de verdade num subprocesso, num arquivo do meu scratchpad, fora do repositório. Comparei o código da base com o do head (rc, chamadas ao `gh`):
- S1: o texto de `docs/reviews/<pedido>.md` copiado para `<tmp>/fora/.forge/pareceres/<pedido>/review.md` e publicado com caminho absoluto. Base: rc 0, 8 chamadas. Head: rc 1, 0 chamadas ("use .forge/pareceres/...").
- S1b: o mesmo, publicado como `../fora/.forge/pareceres/v9/review.md`. Base: rc 0. Head: rc 1, 0 chamadas.
- S2: aprovado e depois reprovado no mesmo caminho, e o aprovado reposto sem hook. Base: rc 0. Head: rc 1, 0 chamadas ("como o último de `.forge/pareceres/v9/review.md`").
- Variantes que acrescentei (todas falham fechado no head e publicavam na base): `.forge/pareceres/<pedido>/review.md` como link simbólico para um arquivo fora da raiz (o `realpath` sai da raiz e o relativo fica vazio); o mesmo caminho como link para `docs/reviews/<pedido>.md` (o relativo resolvido não casa com a forma); e o QA que grava por cima depois do tech-lead (o último registro é de `qa`, e o publicar recusa).
- O que é legítimo continua publicando: o caminho relativo `.forge/pareceres/v9/review.md` (rc 0) e a raiz passada por um link simbólico (rc 0, porque os dois lados passam por `realpath`).

**O que aperta:**
- O registro de outro caminho não vale mais, nem com o mesmo texto e o mesmo papel. Isso fecha a cópia de `docs/reviews/` para `.forge/pareceres/` e o arquivo fora da raiz, inclusive por `..` e por link simbólico.
- Só o último registro do caminho vale. Assim, o veredito superado não volta.
- Se um papel errado gravar por último no caminho, a publicação fica bloqueada até o papel certo regravar.
- Um caminho absoluto chamado com o diretório atual fora da raiz da cópia passa a ser recusado (o `--raiz` padrão é o diretório atual, `bin/forge-check:11161`). Antes, a busca no caminho absoluto casava. A falha é fechada e a mensagem diz a forma certa.

**O que é neutro:**
- A regex vira a constante `PARECER_A_PUBLICAR` com a mesma classe de caracteres. As mensagens de recusa ganham o caminho, e as checagens de contrato, G1.2, M14.1 e `commit:` não mudam.
- `test_forge_pareceres.py:253` passa a gravar no registro de teste o caminho real em vez de `"x"`. Isso só alinha a fixture com o que o hook grava, e o teste não perde força.
- Os M17 e M18 foram movidos para a linha nova e continuam morrendo.
- Worktrees do mesmo repositório gravam o `caminho` relativo a cada uma, num `autoria.jsonl` comum. Por isso, o "último" de `.forge/pareceres/<pedido>/<tipo>.md` é compartilhado entre elas: a gravação mais recente em qualquer worktree decide. Isso não abre caminho novo. Para publicar, o texto ainda precisa ser o que o papel do tipo gravou por último naquele caminho, e o pior caso é recusar e pedir uma regravação.

**O que afrouxa:** nada. Nenhuma checagem sai, nenhuma condição fica mais fraca e nenhum caminho que a base recusava passa a publicar. Concordo com o autor que só aperta. A `catraca` falha por R-CONFORMIDADE ("mudança em bin/forge-check"), à espera do rótulo `afrouxa-regra` do dono, e essa decisão é dele.

**Mutantes:** `bin/forge-mutante tests/mutantes/v0481-g2-publicar-caminho.json`: M38, M39 e M41 morrem por asserção. M40 e M42 morrem por erro do teste declarado (sob o mutante, o publicar segue até o `gh` falso ou quebra em `None`). Morrer por erro é prova mais fraca, mas o comportamento sob guarda é a recusa sem registro, que `test_ponta_a_ponta_recusa_sem_autoria` também prova por asserção. `tests/mutantes/v0481-g2-1-publicar-3.json`: M17 a M20 morrem.

**Lacuna que fica, a mesma de T9 e T10 [B]:** o registro é local, e um agente que escreve direto em `.forge/run/autoria.jsonl`, ou que chama a API com o token, passa por fora do publicar até o G4. O PR não muda isso.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei `python3 -m unittest tests.test_conformidade_pareceres tests.test_forge_pareceres`: 44 OK no head. Com o `bin/forge-check` da base, `tests.test_conformidade_pareceres` dá 3 FAIL, exatamente os 3 testes novos. Rodei também os dois arquivos de mutantes acima e as 8 sondas (scratchpad). Usei o `gh` só para ler checks e logs. Não usei gitleaks nem osv-scanner, porque o diff não traz segredo nem dependência.
