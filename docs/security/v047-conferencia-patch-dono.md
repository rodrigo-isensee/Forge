---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-patch-dono
commit: 1580490eed439198800b81d16df803f439636eaf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047 E1.2 (CONFERENCIA-PATCH-DO-DONO)

E1.16. Head revisado `69bd48632b1bccfb477b3f328bce8feaa8154aa5` (base `a986c292`), contra os controles P1 a P12 e os casos C1 a C15 e C-LEG de `docs/security/v047-e1-ameacas.md` (cópia principal). Diff: `bin/forge-check` (+88 −3), `tests/test_conf_escopo.py` (classe `PatchDoDono`, 8 testes), 3 arquivos de mutantes (23 mutantes), fragmento do changelog.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`bin/forge-check`, em PROTEGIDOS) que abre uma isenção no portão de escopo da conferência de entrega.

## Achados
- A1 (recomendado) bin/forge-check:1840 · P11 incompleto: `e_ancestral(commit, base_sha)` que falha no git (rc 128) vira "não é ancestral" e o commit já na base isenta (sonda S1); separar rc 1 de rc>1 e reprovar com `escopo: o git falhou (patch do dono)`, com teste no C15.
- A2 (recomendado) tests/test_conf_escopo.py:267 · C12 sem teste (arquivo isento segue em classe, gatilhos e parecer) e C13 sem `docs/pedidos/<x>.md` nem `.forge/run/autoria.jsonl`; o código cumpre (P8 por construção, P9 pela sonda S2), falta a trava contra regressão.

## Sondas
- S1 · isencao_do_dono com git mockado: `merge-base --is-ancestor <X> <Base-sha=X>` devolve rc 128 · espera: `escopo: o git falhou (patch do dono)` ou recusa · obtido: `escopo: ok (patch do dono 730a02b, DECISÃO DO DONO exemplo:16)`

## Revalidação por delta (E1.31, head c793d6ea)
Parecer anterior no `69bd4863`; junção com a `develop` (#517 escopo-ponto, #522 pr-hook-prazo) em `c793d6ea`. `forge-check parecer delta` aponta `bin/forge-check` no domínio; o resto do diff do intervalo (`PR-HOOK-PRAZO`, `anexo_implicito`, brief selado, `pedido_dos_pareceres`) veio da `develop`, já revisado lá, e não toca a isenção. O conflito em `bin/forge-check` e `tests/test_conf_escopo.py` foi lido contra `9b2c6474` (diff só da branch: +91 −3 em `bin/forge-check`).
- Ordem dos ramos de `linhas_de_entrega` (:1810-1840 do bloco, ramo final em :2744): `M2 fora` → parecer com autoria → `merge-integracao` → `anexo_implicito` → `anexo do portão` → `else` com `isencao_do_dono`. A isenção é só o último ramo, depois do anexo do portão; arquivo em pasta de parecer, aceite ou oráculo nem chega a ela (`tipo` ou `NUNCA_PATCH_DO_DONO`, P9).
- Bloco `PATCH_DO_DONO` .. `isencao_do_dono` byte a byte igual ao do `69bd4863` (sha256 do trecho idêntico nos dois commits): P1 a P12 seguem como conferidos acima, sem regressão. `patches_do_dono` e a linha de aviso da forma (P3) continuam antes do laço.
- Nenhum achado novo; A1 e A2 seguem recomendados (código e teste inalterados).

## Revalidação por delta (E1.38, head 1580490e)
Parecer anterior no `c793d6ea`. `forge-check parecer delta` (intervalo `c793d6ea..1580490e`, sem o que veio da `develop`): no domínio só `bin/forge-check`; fora, `tests/test_conf_escopo.py`. O resto do intervalo (`TRAVA-AGENTE-MORTO`, `hooks/agentes.py`, mutantes) veio da `develop` (#523), revisado lá.
- `bin/forge-check:1863` (E1.33): o `pedido_id` do rótulo `escopo: ok (patch do dono ...)` passa por `sem_controle` (:2774; controle, bidi e U+2028/2029 viram um espaço). Muda só a saída; a decisão da isenção (P1 a P11) não é tocada. Fecha o P12 para o id do pedido, que saía cru. Nenhum achado novo.
- `tests/test_conf_escopo.py`: o c11 troca `README.md` por `LEIAME.md` (nome sintético fora de TEXTO); não afrouxa o teste.
- A1 e A2 seguem recomendados (código e teste da isenção inalterados).
Suíte: `python3 -m unittest tests.test_conf_escopo.PatchDoDono` no `1580490e`: 8 testes, OK em 42,2 s. CI do PR #524 neste head (run 43438578467): `bateria (passos)` vermelha no passo "Parecer de review (e de QA para a homolog) quando o PR toca código que governa os agentes" (exige pareceres da junção com `hooks/agentes.py` da #523, fora do meu domínio); `bateria` e `bateria (python 3.14)` falham por consequência. Não vejo falha em teste da isenção. CI verde é condição do merge (R-REVIEW), do tech-lead.

## Detalhe dos achados
**Conferência dos controles (head 69bd4863):**
- P1: a declaração vem só do pedido lido por `caminho_do_pedido` (mesma fonte do `desde_valido`), exige a linha de forma exata no `## Histórico` (`PATCH_DO_DONO`, :1691) e uma linha de decisão pela regra única `linhas_de_decisao` citando sha40 e caminho como palavras inteiras (`decisao_do_patch`, :1713). Nada da branch, do brief, de commit ou de ambiente declara. Sonda: a linha `DECISÃO DO DONO` com prefixo de data dentro do `## Histórico` também vale; é a regra de decisão da fábrica (DECISAO-ANCORA), mesmo residual do aceite de QA, não achado.
- P2: `pedido_na_entrega(base_sha, head)` antes da decisão (:1753), com falha do git fechada (`cod or saida`). C4 em teste.
- P3: `[0-9a-f]{40}` ancorado e `sha_do_commit(X) == X` (tag e blob recusados); linha fora da forma sai com aviso visível (:2540-2542). C5 em teste.
- P4: blob e modo do head comparados com os de X por `ls-tree --literal-pathspecs` (:1720-1768). C6 e C7 em teste; mutantes de blob e de modo.
- P5: X ancestral do head e não ancestral do Base-sha (:1745). C8 e C9 em teste. Ver A1 (falha do git no segundo teste).
- P6: o nome vem do diff e casa por chave exata do dicionário (sem `fnmatch`/`startswith`); `caminho_isentavel` recusa curinga, barra invertida, controle (inclusive bidi), parte vazia, `.` e `..`; symlink (120000) e submódulo recusados. C10 em teste; sonda S2 abaixo.
- P7: a isenção é por arquivo e exige que X altere aquele caminho (`diff X^1 X`); os outros arquivos de X seguem o escopo comum. C11 em teste.
- P8: a mudança só toca a linha `escopo:` em `linhas_de_entrega` (:2569-2572); `classe_da_entrega`, `e_codigo`, gatilhos, PROTEGIDOS e `afrouxa-regra` não leem essa linha. Ver A2.
- P9: `NUNCA_PATCH_DO_DONO` (:1692) = `docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/` (cobre `docs/security/aceites/`), `docs/pedidos/`, `tests/test_oraculo_`, `.forge/run/autoria.jsonl`. Sonda S2 (fora do bloco, não prova bloqueante): `caminho_isentavel` devolve False para `.forge/run/autoria.jsonl`, `docs/pedidos/x.md`, `docs/security/x.md`, `docs/devops/x.md`, `docs/qa/x.md`, `a\b`, `a/<U+202E>b`, `/abs`, `a/`.
- P10: `rev-list --parents -n1` com exatamente um pai; merge e commit raiz recusados. C14 em teste.
- P11: `rev-list`, `diff` e `ls-tree` que falham reprovam com `escopo: o git falhou (patch do dono)`; `sha_do_commit` e `e_ancestral(X, head)` falham fechado. Exceção: A1.
- P12: rótulo `escopo: ok (patch do dono <sha7>, DECISÃO DO DONO <pedido>:<linha>) <caminho>` e aviso por recusa com o motivo; nomes por `nome_seguro`, linha do pedido por `linha_legivel`.

**A1.** Evidência: `bin/forge-check:1745` e `e_ancestral` (:1780, `== 0`). Caminho de ataque: precisa que o `merge-base` falhe só no teste contra o Base-sha (objeto faltando, repositório corrompido), e ainda assim a isenção exige a linha `DECISÃO DO DONO` com o sha40 e o caminho e o blob de X no head; nenhum ator do time provoca isso de modo seletivo. Severidade: baixa. Correção mínima: em `isencao_do_dono`, chamar `git(raiz, "merge-base", "--is-ancestor", commit, base_sha)` e tratar rc diferente de 0 e 1 como `falhou`; caso no `test_c15` (mock do `merge-base`). Esforço P. Dono: tech-lead.

**A2.** Evidência: `tests/test_conf_escopo.py:266` (nunca-isenta só com `docs/reviews/`, `docs/security/aceites/` e `tests/test_oraculo_`); nenhum teste do C12. Caminho: regressão futura que faça a isenção pular classe ou gatilho passaria sem teste vermelho. Severidade: baixa. Correção mínima: no C-LEG, conferir que `classe` e `gatilhos_seguranca` da entrega seguem iguais com e sem a declaração; no C13, incluir `docs/pedidos/x.md` (pela função `caminho_isentavel`, porque o C4 já recusa antes) e `.forge/run/autoria.jsonl`. Esforço P. Dono: tech-lead (ou qa-engineer).

## Riscos aceitos e ferramentas
Residual já registrado no modelo de ameaças (não muda aqui): a linha `DECISÃO DO DONO` é transcrita pelo Jarvis, não assinada pelo dono; a defesa real é P4 somado a P8. Nenhum risco novo pede aceite.

Suíte (revalidação): `python3 -m unittest tests.test_conf_escopo.PatchDoDono` no `c793d6ea`: 8 testes, OK em 70,8 s (carga ~13). O PR #524 (rascunho) mostra `bateria`, `bateria (passos)`, `bateria (python 3.14)` e `catraca` vermelhos neste head; não consegui ler o log (cache do `gh` somente leitura), então não afirmo a causa: o CI verde é condição do merge (R-REVIEW) e fica ao tech-lead. Da rodada anterior: sem PR, sem CI; rodados só os testes afetados, `python3 -m unittest tests.test_conf_escopo.PatchDoDono` (8 testes, OK em 21,7 s), e as sondas S1 e S2 na mesma estrutura de teste (arquivo temporário, fora da branch). Mutantes declarados (23) lidos contra a lista do modelo de ameaças: todos os da lista estão presentes; não os executei (carga da máquina, diretriz 15), o CI do PR os roda. Ferramentas de varredura de segredo e SAST fora do PATH: lacuna registrada; o diff não traz segredo nem dependência.
