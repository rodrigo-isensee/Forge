---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-forge-check
commit: fca6174f1a9169a934c94484fa60d48d04085c94
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E2.3, branch melhoria/v0478-guardas-forge-check; revalidado na E2.7)

Diff `4182a6b9..63326514`: 2 commits (`f8b81f8f` FC-PR-PARECER-FORJADO, `63326514` FILTROS-L08-G2-ORIGIN-LOCAL), cerca de 47 linhas de código em `bin/forge-check` (teto H1 respeitado), 2 módulos de teste novos, 3 testes existentes ajustados ao aperto, mapa do `bin/forge-testes` e fragmento em `changelog.d/`.

## Achados
- A1 (recomendado) bin/forge-check:1987 · Sonda no repositório: 3 grupos históricos legítimos (anti-alucinacao-portao e -regras: review do autor e independente; lote-leitura-hook: `-desenho.md`) dariam "pareceres divergentes". Nenhum fluxo atual os gera, mas a mensagem poderia nomear o caso. R-REVIEW
- A2 (recomendado) bin/forge-check:2644 · `base_sem_ancora` só olha merges (2 pais); o squash da base sem âncora (L08, um pai) segue no escopo sem a linha informativa. O comportamento está certo, só falta explicar o motivo ao autor.
- A3 (recomendado) docs/pedidos/v0478.md:29 · pendente: a parte do `forge-check pr` do CONFIG-TETO-SEM-GUARDA, listada na E2.1, não tem commit nesta branch nem marca de corte no brief; registre o corte (R-DECISAO) ou abra uma etapa própria.

## Sondas

## Parecer
Aprovado. Os dois cartões fazem o que pedem.

- **FC-PR-PARECER-FORJADO:** `pareceres_divergentes` agrupa pela branch do parecer vigente e recusa divergência em `parecer`, `revisor` ou `commit`, nos exigidos (`cmd_pr`) e nos não exigidos (`nao_exigidos_que_nao_aprovam`, com `continue`, então o aprovado forjado não esconde o reprovado). Sem `branch` (catraca e promoção), as outras branches do pedido ficam fora do grupo, e um teste cobre isso.
- **FILTROS-L08-G2-ORIGIN-LOCAL:** `na_base` exige que o commit também descenda do Base-sha ou de uma âncora selada depois, nos três filtros (L08, G2 e E2). `ancoras=None` mantém o `entrega` manual como antes. O autor não consegue tornar um commit seu ancestral de um Base-sha selado, então a reescrita da `origin/<base>` deixa de esconder arquivo.
- **O aperto é intencional:** sem âncora, o merge real da develop passa a reprovar com o que ela trouxe no escopo (`test_merge_base_sem_ancora_fica_o_base_sha` foi de rc 0 para 1). A linha `escopo: merge da <base> sem âncora` explica a causa, e o remédio é o Jarvis selar um brief com o Base-sha novo.

Regras de leitura (checklist `engineering-practices`): os nomes dizem o que fazem; as funções são curtas, com docstring que cita o cartão; os commits estão limpos em Conventional Commits; nada afrouxa. Os 3 achados são recomendações e não devolvem a entrega (R-REVIEW).

Ferramentas, rodadas pelo revisor no head 63326514, sem a suíte inteira, que fica para o CI do PR:
- os módulos novos e os testes tocados (`test_fc_pr_parecer_forjado`, `test_filtros_l08_g2_ancora`, `test_conferida_por_branch`, `test_selo_e_entrega.MergeDaBaseDepoisDoBrief` e `.JuncaoLimpa`): `Ran 32 tests ... OK`;
- `bin/forge-mutante --base 4182a6b9`, nas duas specs: M1 a M12 `morreu`, rc=0;
- `--cobertura`: as condições mudadas estão todas cobertas (a linha `não coberto: tests/pesos-d4.json` é um arquivo de dados, não uma guarda).

## Revalidação (E2.7, head fca6174f)
Lido só `forge-check parecer delta docs/reviews/v0478-guardas-forge-check.md`: intervalo `63326514..fca6174f`, escopo sem o que veio da develop. No domínio ficam 3 arquivos: `bin/forge-testes`, `tests/pesos-d4.json` e `tests/test_testes_tocados.py`. O parecer do QA (`fee3beb6`) e o merge `a3a92343` não mudam código.

- **Conflito em `tests/test_testes_tocados.py` (`git show --cc fca6174f`):** a resolução junta os dois lados. Da develop vêm o `assertIn("test_indice_forge")` e o filtro `m != "test_indice_forge"` na contagem. Da branch vem o total 101, que soma os 2 módulos de E2.1. A contagem continua sendo a dos módulos do `forge-check`, e o índice fica fora dela.
- **`bin/forge-testes` e `tests/pesos-d4.json`:** contra a develop (`git diff 0c47762a fca6174f`), sobram só as 2 entradas de `FORGE_CHECK` e o peso de `test_filtros_l08_g2_ancora`, que já foram revisados. O resto do delta veio da develop sem mudança (H7 `teste_do_indice`, peso de `test_ferramentas_portoes`).
- **Teste rodado no head fca6174f:** `test_testes_tocados.Mapa`, `.MapaCobreOQueOsTestesLeem` e `.NaoEPortao` deram `Ran 32 tests in 15.184s OK`. A suíte inteira roda no CI do PR.

Continua aprovado. Os achados A1 a A3 seguem como recomendações, e o delta não traz achado novo.
