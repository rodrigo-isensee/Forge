---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: 6c709157b28682ed39bab0663bdd8989753e9790
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (#902, R-QA-VOLTAS-ALINHADA), volta E14.80

Revalidação por delta (E14.90), de `e871982c..6c709157`. Li o `forge-check parecer delta`, que tira o que veio da develop. No domínio estão `agents/jarvis.md`, `bin/forge-check` e `bin/forge-testes`. Fora do domínio ficam `tests/mutantes/v0480-g1-1-uma-volta-3.json` e `tests/pesos-d4.json`. A rodada anterior está no git.

O merge `98c9dfde` (pais `763ab0f9` e `020e4af7`) teve conflito de conteúdo em dois arquivos: `agents/jarvis.md:30-31` e `bin/forge-check:10814`. Comparei a árvore do merge com a árvore com os marcadores (`git merge-tree`). O resto entrou igual ao automático. Na resolução, `jarvis.md` ficou com o passo 5 da develop (`--worktree <cópia>`) e com o passo 6 da branch (`voltas sem teto`), que é a mudança deste PR. Em `forge-check`, os dois lados entraram: `testes_enfraquecidos_da_volta` da branch e o `prova_do_pronto` da develop (D2-NO-BRIEF), que vale para a etapa `codigo`. Nenhum dos dois lados perdeu linha.

- ci: 6c709157b28682ed39bab0663bdd8989753e9790 verde

As 10 partes da suíte (3.12 e 3.14), `bateria (python 3.14)`, `passos`, `verificações longas`, `instalação`, `teto de pulados` e `árvore já provada` estão verdes no head exato. Há três vermelhos, e li o log de cada um. `bateria (pareceres)` falha porque os três pareceres do head anterior estão `reprovado`, e é isto que esta rodada regrava. O agregado `bateria` cai por causa dela. A `catraca` mostra os mesmos itens da rodada anterior, que pedem o rótulo `afrouxa-regra` do dono: cinco testes apagados, as guardas `recusa_da_volta` e `voltas_autorizadas` e o próprio `bin/forge-check`. Ela também mostra um item novo, `R-CONTRIB`: o corpo do PR está sem `## Projeto de origem`. É texto do PR e não é de segurança.

Rodado aqui, só no que foi tocado: `tests.test_volta_por_delta`, `tests.test_volta_alinhada` e `tests.test_voltas` (168 testes, OK, 1 pulado já existente); `tests.test_forge.SaidaSanitizada` (8, OK); `tests.test_forge_mutante.ConferirTodas` (4, OK).

Gatilhos: controle do Forge (`bin/forge-check`: mensagem da volta e conferência da entrega), texto de agente que governa as voltas.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:** `bin/forge-check:4751` passa `real` e `texto_da_volta` por `sem_controle`. A saída da volta fica sanitizada, e o guarda do abuso 18 volta a ficar verde. Na resolução do conflito, `bin/forge-check:10814-10817` mantém as duas conferências da entrega (`testes_enfraquecidos_da_volta` e `prova_do_pronto`), sem que uma substitua a outra.
- **Neutro:** a saída de M21 e M23 de `v0480-g1-1-uma-volta-3.json`. O M23 mutava uma regex que já não existe na fonte. O teste do M21 foi apagado no `e56ec5899`, a volta já revisada e coberta pela DECISÃO DO DONO de 25/11 17:07. A sonda S90-M21 (registro) confirma que o fallback de `bin/forge-check:4760` sobrevive ao mutante. Esse fallback, porém, não tem caminho em produção: o único chamador (`:9298`) sempre passa `cobradas`, que vem de `decisoes_cobradas`. Também é neutro o passo 5 de `jarvis.md`, que veio da develop igual.
- **Afrouxa:** nada novo neste delta. O fim do teto (`jarvis.md:31` `voltas sem teto`) é o da rodada anterior, autorizado pela ordem das 17:07, e o rótulo continua sendo ato do dono.

## Detalhe dos achados
**Estado dos achados anteriores.** A4 (guarda de saída sanitizada, `real` cru): resolvido em `bin/forge-check:4751`. `tests.test_forge.SaidaSanitizada` passa aqui e no CI (partes 3/5). O M23 fora da fonte, apontado fora do domínio na rodada anterior, também está resolvido: `ConferirTodas` passa, e a parte 4/5 está verde.

**Sonda de registro, sem bloqueante:** S90-M21 é a spec `/root/.forge-contrib/wt/_sec90-m21.json`, que troca o fallback de `:4760` por `{"fontes": []}`. Rodei `bin/forge-mutante` com ela, e o resultado foi `sem veredito`, porque os testes que rodaram não mataram o mutante. Não há caminho de ataque, já que o fallback é inalcançável pelo único chamador. Vai em `Melhoria vista:`: remover o fallback morto ou cobri-lo com um teste.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: leitura do diff, `git merge-tree` para comparar a resolução, os testes dos módulos tocados, `bin/forge-mutante` e os logs do CI. Faltam no ambiente gitleaks, semgrep, zizmor, actionlint e osv-scanner (lacuna). O delta não traz workflow, dependência nem segredo.
