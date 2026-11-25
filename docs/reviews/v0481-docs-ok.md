---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 9fa5f83278cfea50921a8fbd156766067450d354
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.19, code review do #892)

Diff `220ba3fa..9fa5f832`: +8 e -2 em `bin/forge-check` (dentro do teto H1, um comportamento por parte), testes em `tests/test_forge.py`, `tests/test_forge_copia.py` e `tests/test_volta_por_delta.py`, skill `checagem-do-brief/por-tema.md`, fragmento `changelog.d/v0481-docs-ok.md` e a spec `tests/mutantes/v0481-docs-ok.json`. Clone de revisão criado com `forge-copia clone ... --revisao` (a cópia da própria branch), em `9fa5f832`.

## Achados
- A1 (recomendado) bin/forge-check:11241 · a linha do `gravar` mudou só no espaço e ficou `gravar =not ...` (falta o espaço depois do `=`); volte ao `gravar = not`, que tira a linha do diff sem mudar o comportamento.

## Parecer
**Aprovado.**

- **`docs: ok`:** em `executar`, a linha sai só com `a.cmd == "docs"` e a lista de violações vazia, depois das violações; o `return 1 if violacoes else 0` não mudou, então o rc é o mesmo e nada que barra hoje deixa de barrar. O `cmd_docs` não imprime violação por fora da lista (os prints dele vão ao stderr, avisos). Sonda: `forge-check docs nao-existe.md` dá a violação e rc=1, sem o `ok`; `forge-check docs` na branch dá `docs: ok` e rc=0.
- **Chamadores:** nenhum código lê o stdout do `docs`. O hook `conformidade` só lista `forge-check docs` como comando permitido; `forge-fechar`, a catraca e o pre-push chamam o `pr`, não o `docs`; o PQ gerado no brief do portão espera só `rc=0`. Nenhum doc ou agente diz que o `docs` aprovado é silencioso.
- **Catraca, valor esperado trocado:** conferi os 10 testes que ela lista (`DocsPareceresPedidoECaminho.test_linha_de_comando_com_arquivo`, `ForgeCheck.test_docs_validos_e_ignorados`, `test_qa_medio_com_aceite_vale`, `test_qa_medio_sem_aceite_vale`, `ForgeUpgrade.test_migra_e_segunda_vez_nao_muda_nada`, `BriefDeVolta.test_docs_cobra_o_bloco_de_quem_adotou_o_formato`, `DocsEstritoNoDelta` (2), `ProvaDaSuite.test_bateria_metodo_e_outro_tipo_passam`, `Sondas.test_linha_boa_passa_e_parecer_sem_bloco_nao_muda`): todos trocam `(0, "")` por `(0, "docs: ok\n")`, a igualdade exata segue (nenhum vira `assertIn` nem perde asserção), e o caso de reprovação ganhou `assertNotIn("docs: ok", ...)`. Troca legítima.
- **Brief do portão:** o novo ramo entra só com `etapa in ETAPAS_DE_PARECER` (review, segurança, QA) e manda `forge-copia clone ... --revisao`; o `elif` mantém a linha de hoje para as outras etapas. O teste novo cobre as três etapas e o `codigo` sem `--revisao`. A skill `por-tema.md` diz o mesmo.
- **Mutantes:** `bin/forge-mutante --processos 1 tests/mutantes/v0481-docs-ok.json`: M1 a M4 morreram (`forge-check:11239`, `9731`, `9735`); `--cobertura --base 220ba3fa`: as guardas mudadas cobertas pela spec. Testes tocados rodados no clone: 56, OK.
- **Ferramentas (citadas, não refeitas):** suíte no CI do PR #892, ainda em andamento no head `9fa5f832`; a "catraca" e a "bateria (pareceres)" estão vermelhas porque faltam os pareceres e porque `bin/forge-check` é controle (R-CONFORMIDADE): o rótulo é do dono, depois do último push.
