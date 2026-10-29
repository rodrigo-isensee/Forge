---
tipo: review
contrato: 1
pedido: t1-conf-escopo
branch: melhoria/t1-conf-escopo
commit: 5d1e769b0165f2e892f7d51b2569c5f8cb34b86b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: t1-conf-escopo (volta 1 e merge da develop f3f63f9, T1-CONF-ESCOPO-REV)

Revalidação por delta do parecer anterior (`4b7387e`, head `b9426d8`, reprovado por A1). Base do pedido: `87e32b6`; develop atual `f3f63f9`.

## Achados
- A3 (recomendado) agents/conferente.md:83 · o texto ainda diz "com review, QA e segurança aprovados", e a docstring em bin/forge-check:1010 ainda diz "review, QA e segurança do diff"; o `pr` exige QA só sem isenção e segurança só com gatilho: diga "os pareceres que o `forge-check pr` exige" (o comentário da linha 1122 já foi corrigido)
- A4 (recomendado) tests/test_conf_escopo.py:61 · falta a linha em branco entre `test_merge_commit_sem_parecer_reprova` e `test_aceite_e_config_nunca_sao_anexo_nem_com_pareceres_aprovados` (PEP 8); o resto do espaçamento foi corrigido

## Delta lido
`bin/forge-check delta --parecer docs/reviews/t1-conf-escopo.md` deu o intervalo `b9426d8..5d1e769`. Do intervalo, li inteiros os commits do autor `f8b0962`, `ccca64d`, `91efab7`, `fd5bbcf` e `5d1e769`, e a resolução do merge `76a27ee` (`git show --cc`).

O que a develop trouxe por `f3f63f9` (T6T3-MENSAGEM #367, LOTE-0307-A #364) foi revisado nos PRs de origem e conta aqui como **já lido**: `agents/jarvis.md`, `bin/forge-fechar`, `docs/fechamento-integrador.md`, os `_modelo.md`, os fragmentos `changelog.d/lote-0307-a.md` e `changelog.d/t6t3-mensagem.md`, `tests/mutantes/lote-0307-a.json`, `tests/mutantes/t6t3-mensagem.json`, `tests/test_fechar_base_andou.py`, `tests/test_mensagem_conferente.py` e as linhas da develop em `bin/forge-check` (12, 4652-4722, 5297-5302).

Do diff `87e32b6...b9426d8`, o que ficou fora do delta também conta como já lido no parecer anterior.

## Parecer
Aprovado. O bloqueante A1 foi corrigido, e o A2 e o A3 da segurança também. O merge da develop está limpo. Ficam dois achados recomendados (A3 e A4), que não devolvem a entrega.

**A1 (bloqueante anterior): resolvido.** Em bin/forge-check:1122, o ramo do E1 agora exige `not nome.startswith(ACEITES_DO_USUARIO) and nome != "tests/config.json"`; os dois arquivos seguem `escopo: confira`.
- O teste `MergeIntegracao.test_aceite_e_config_nunca_sao_anexo_nem_com_pareceres_aprovados` cobre os dois caminhos, a ref viva e o mergeCommit, com os três pareceres válidos, e afirma que `notas.md` continua `ok`.
- O agents/conferente.md:83 cita as duas exceções e diz que o rótulo não atesta o parecer.

**A2 (recomendado anterior, mesmo ponto da segurança): resolvido.** Em bin/forge-check:1013-1016:
- O filtro de `docs/reviews/` vem antes do `git show`, e só um pedido único é aceito.
- Dois pedidos dão `None` e reprovam. Parecer ilegível entra como `None` no conjunto e também reprova. As duas saídas são conservadoras.
- O `min(pedidos)` com um elemento equivale ao `pop()`.
- A troca de `a` por `z` no teste faz o M20 (`>= 1`) escolher `x`, que tem o review aprovado. Assim o mutante só morre pela condição do pedido único, e o teste deixa de ser vácuo.

**A3 da segurança (parecer trazido por merge com frontmatter válido): conferido.** Em bin/forge-check:1037-1040, o parecer só vale com o `tipo` da pasta, `parecer` `aprovado|reprovado` e `branch: melhoria/<slug>`, com um teste por caso negativo (subTest). O fallback `{"tipo": None}` repete o estilo de `pedido_do_parecer` e equivale a `{}`; a isenção dele está declarada na spec, com motivo.

**Mutantes M18 a M23, e M1/M2 ajustados ao A2.** Rodei `bin/forge-mutante` nas duas specs, no head `5d1e769`:
- `t1-conf-escopo-2.json`: M17 a M23, todos "morreu", rc=0.
- `t1-conf-escopo.json`: M1 a M16, todos "morreu", rc=0. M1 e M2 seguem o código novo.

**Merge da develop f3f63f9 (`76a27ee`).**
- `bin/forge-check`: auto-merge sem conflito. O diff `f3f63f9..76a27ee` desse arquivo traz exatamente as linhas do T1 de `87e32b6..fd5bbcf` (comparei os dois patches com `diff`: iguais).
- `bin/forge-testes`: a resolução mantém os dois módulos novos no mapa, `test_conf_escopo` (do T1) e `test_mensagem_conferente` (da develop).
- `tests/test_testes_tocados.py`: a contagem vai de 29 para 30, o que confere (o T1 e a develop somam um módulo cada à base de 28).
- `agents/conferente.md`: a develop juntou `**O que conferir:**` à linha anterior, e o parágrafo do T1 entrou intacto.

**Linha em branco tirada de agents/conferente.md (`5d1e769`).** É um commit próprio, que só remove a linha vazia antes de `## Tabela de etapas`, sem mudar palavra. O título ATX continua título em CommonMark. O arquivo ficou com 110 linhas (`wc -l`), dentro de `Orcamento.test_tamanho_dos_prompts`, e `**Entregas paralelas**` segue abrindo a linha.

**Testes do item.** `python3 -m unittest tests.test_conf_escopo tests.test_testes_tocados tests.test_forge.Orcamento`: 92 testes, OK. A suíte completa fica com o pre-push e o CI do PR (decisão do dono de 2026-10-24, corte 1).

**Teto (M14).** `git diff --numstat --no-renames origin/develop...5d1e769` dá 184 linhas, acima de 150:
- `bin/forge-check`: 52
- `bin/forge-testes`: 2
- `tests/test_conf_escopo.py`: 128
- `tests/test_testes_tocados.py`: 2

Aceito a exceção pela DECISÃO TÉCNICA 2026-10-29 13:39, porque correção de bloqueante não se divide em outro lote. O PR não toca `hooks/` nem caminho de `PROTEGIDOS`, e fica abaixo das 400 linhas do jarvis.md. A exceção só vale com a linha `teto: excedido, 184 linhas, correção do bloqueante A1 na volta 1 (DECISÃO TÉCNICA 2026-10-29 13:39)` no corpo do PR; sem ela, o achado volta como bloqueante (decisão M14). O PR carrega um comportamento só: o escopo do conferente na merge-integracao, com os anexos implícitos.

**Classes.** Nesta rodada não há linha AR nova (DECISÃO TÉCNICA 2026-10-29 15:28):
- O A1 anterior é da classe "exceção de proteção perdida em ramo novo de aceite"; não se repetiu neste pedido depois da correção.
- O A3 é da classe "texto promete mais que o código", parente da AR-9 (limite-antigo-no-texto).
- O A4 é formatação.

**PA-7, item a item (`docs/engineering/achados-recorrentes.md`).**
- AR-1: o ramo do A1, o A2 e o A3 têm mutante (M18 a M23), todos mortos.
- AR-2: o ramo `None` do A2 tem teste de comportamento.
- AR-3, AR-5 e AR-7: não há trava de ambiente, `python` sem `-I` nem pasta do git no delta.
- AR-4: os testes usam o repositório temporário do `Repositorio` e o `guarda_git`.
- AR-6 e AR-8: o delta não tem shell nem `cd`.
- AR-9: ver o A3.

**Ferramentas e outros portões.** O Forge não tem `docs/engineering/praticas.md`. A suíte, o shellcheck e a validação do plugin rodam no pre-push e no CI do PR; não os refaço aqui. A segurança (`docs/security/t1-conf-escopo.md`) e o QA (`docs/qa/t1-conf-escopo.md`) revalidam em paralelo nesta rodada e ficam citados aqui, sem refazer.
