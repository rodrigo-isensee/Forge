---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: 46000ed50e0089fb2818c440c2c5355a6d38dd10
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (#902, R-QA-VOLTAS-ALINHADA, E14.44 e E14.59)

1ª rodada completa (E14.62), diff `34ab6714..46000ed5` (merge-base com a develop), 13 arquivos.

- ci: 46000ed50e0089fb2818c440c2c5355a6d38dd10 verde

O CI do PR no head exato tem verdes as 10 partes da suíte (3.12 e 3.14), os tetos de pulados, a instalação, os passos, as verificações longas e a árvore. Só `bateria (pareceres)`, `bateria` e `catraca` falham, e a linha do CI os deixa de fora. Pelo log, `bateria (pareceres)` falha só pela falta do parecer de review. A `catraca` falha só por duas violações, e as duas pedem o rótulo `afrouxa-regra` do dono: (1) `test_volta_dois_so_com_decisao_do_dono_que_cita_a_branch` foi renomeado para `test_volta_quatro_...`; (2) a mudança em `bin/forge-check`, controle que sempre pede o rótulo. Os cinco avisos de "valor esperado trocado" (`test_conferencia_recusa_a_numeracao_contornada`, `test_conferencia_sem_cobradas_le_as_decisoes_do_pedido`, `test_sem_branch_nenhuma_decisao_autoriza`, `test_so_a_forma_canonica_autoriza_e_uma_linha_vale_uma_volta`, `test_volta_conta_o_item_e_nao_a_cadeia`) foram conferidos: em cada um, o valor sobe 2 (1→3, 2→4, 3→5) e acompanha o teto novo. A recusa continua provada no novo limite, e a falha fechada sem branch continua em 1.

Rodado aqui, só nos módulos tocados: `tests.test_volta_alinhada` e `tests.test_voltas` (51 testes, OK); `BriefDeVolta` de `tests.test_volta_por_delta` (35 testes, OK, junto com as sondas); `bin/forge-mutante` nas duas specs novas, com VA-M1 a VA-M12 mortos.

Gatilhos: controle do Forge (`bin/forge-check`: teto de voltas, conferência do brief e da entrega), regra com ID (`R-QA`), texto de agente e de skill que governa as voltas.

## O que aperta, o que é neutro e o que afrouxa
- **Afrouxa:** contra a base, o teto sem o dono sobe de 1 para 3 voltas (`bin/forge-check:4437`, `voltas_autorizadas`), e a 2ª e a 3ª saem sem `DECISÃO DO DONO`. O dono autorizou isso (ORDEM DO DONO 25/11 07:31 e 07:52). Ainda assim é afrouxamento de regra, e por isso a catraca pede o rótulo `afrouxa-regra` do dono.
- **Aperta:** (a) da 3ª volta em diante, a conferência da entrega recusa teste removido ou enfraquecido no diff da volta, com falha fechada quando falta a catraca ou o git falha (`bin/forge-check:4462-4474`, `:10625`); (b) a conferência do brief da 3ª volta exige o texto da restrição (`:4675`); (c) brief `Tipo: codigo` numa branch que já tem parecer `reprovado` é recusado sem `Volta-de:` (`:9147`). O (c) tem o furo descrito no A2.
- **Neutro:** a linha `test_volta_alinhada` no mapa de `bin/forge-testes` e em `tests/pesos-d4.json` (E14.59); o fragmento do changelog; as specs `v0480-g1-1-uma-volta*.json`, ajustadas à constante nova sem perder guarda; os textos de `R-QA`, `agents/jarvis.md` e da skill, que acompanham a ferramenta (a divergência com a ordem em vigor está no A1).

## Achados
- A1 (bloqueante) docs/regras/R-QA.md:17 · Texto e ferramenta seguem a ordem das 07:31, não a das 17:07: o R-QA, o jarvis.md:31 e a skill fixam um teto de 3 voltas, e o forge-check:4506 recusa a 4ª e oferece cortar o item. A ordem em vigor manda resolver sem teto e, da 4ª volta em diante, juntar o tech-lead e o revisor que reprovou.
- A2 (bloqueante) bin/forge-check:9147 · A contagem sem Volta-de só olha o brief com `Tipo: codigo`. Brief à mão sem `Tipo:` (fica desconhecido) ou com `Tipo: volta` e sem Volta-de, numa branch com parecer reprovado, passa rc 0: volta fora do teto e da restrição da 3ª (S1, S2).
- A3 (recomendado) bin/forge-check:4471 · A restrição da 3ª volta mede só somas globais (testes, asserções, pulos, vazios). Tirar a asserção de um teste e pôr `assert True` em outro passa com lista vazia, e a medida por função da catraca também não acusa (S4).

## Sondas
- S1 · conferir na branch melhoria/x (parecer reprovado em docs/reviews/p1.md) o brief tests/fixtures/brief/volta-anterior.md sem linha Tipo, ref melhoria/x · espera: rc 1 e "já tem parecer reprovado" · obtido: rc 0, sem a linha volta:
- S2 · o mesmo brief com "Tipo: volta" e sem Volta-de, ref melhoria/x · espera: rc 1 e "já tem parecer reprovado" · obtido: rc 0, nenhuma linha volta:
- S3 · controle: o mesmo brief com "Tipo: codigo", ref melhoria/x · espera: rc 1 e "já tem parecer reprovado" · obtido: rc 1 e "já tem parecer reprovado"
- S4 · testes_enfraquecidos_da_volta com "(volta 3)" sobre test_b de "assert 2" para "pass; return" e test_a com "assert True" a mais · espera: linha (R-QA) que reprova · obtido: [] (e regra_testes_afrouxados vazia)

## Detalhe dos achados
As sondas estão em `/root/.forge-contrib/wt/_sec72-v0481-voltas-sonda.py`, numa subclasse de `BriefDeVolta` (`python3 -I <sonda> <clone> Sondas`).

**A1 (requisito, ordem em vigor).** Evidência: `docs/regras/R-QA.md:17`, `agents/jarvis.md:31`, `skills/briefs-e-conferencia/autor-ate-o-merge.md:10`, `bin/forge-check:4437` e `:4506-4509`; o teste `tests/test_volta_por_delta.py:994` prova a recusa da 4ª e a opção "cortar o item e reabrir menor". A DECISÃO DO DONO de 25/11 17:07 (docs/pedidos/v0481.md, bloco de decisões) troca o corte por "resolver, com quantas voltas forem precisas" e diz que, da 4ª volta em diante, o tech-lead e o revisor que reprovou trabalham juntos. A restrição da 3ª (só corrige o apontado), da ordem das 07:31, segue em vigor e está certa no diff. Hoje, a 4ª volta exige uma decisão do dono que a ordem dispensou e oferece o corte que ela revogou. Pelo lado da segurança, a divergência é para mais restrição, não para menos. Mesmo assim, a regra escrita (texto único, ADR 0002) contradiz a ordem em vigor e travaria os PRs que estão na 4ª volta. Severidade: média (requisito). Correção mínima: no R-QA, no jarvis.md e na skill, trocar o teto pela regra das 17:07 (sem última volta; da 4ª em diante, tech-lead e revisor juntos; a restrição da 3ª vale da 3ª em diante); em `recusa_da_volta`, deixar de oferecer o corte e, da 4ª em diante, cobrar no brief a marca do trabalho conjunto em vez da `DECISÃO DO DONO`, ou não recusar. Manter a contagem por `Volta-de:`, que é o que dispara a restrição. A forma da marca é decisão do time; o conteúdo é do dono. Esforço: M. Dono: tech-lead (autor do #902).

**A2 (controle contornável, requisito do item).** Evidência: `bin/forge-check:9147`; `tipo_do_brief` (`:2806`) devolve `desconhecido` para brief sem `Tipo:` válido e de destino autor, e `volta` para o `Tipo: volta` gravado sem `Volta-de:`. Caminho de ataque: o Jarvis, ou quem escreve o brief à mão, despacha a volta como brief novo de código sem `Tipo:` (foi o ERRO-JARVIS das 07:33 que originou este item) ou com `Tipo: volta` sem `Volta-de:`. A conferência passa, a volta não entra no teto, e a entrega não a vê como 3ª: o brief não tem `(volta N)`, então `testes_enfraquecidos_da_volta` não mede nada. Provado por S1 e S2, com S3 de controle. Severidade: média (o desvio de contagem é justamente o que o item fecha). Correção mínima: inverter para lista de exclusão, `tipo_do_brief(texto) not in ("review", "qa", "merge", "ato-github")`, para que `codigo`, `volta` sem `Volta-de:` e `desconhecido` recusem. Somar um teste com os dois casos de S1 e S2 e um mutante que volte a `== "codigo"`. O VA-M5 atual (`!= "volta"`) continua morto com a lista de exclusão. Esforço: P. Dono: tech-lead.

**A3 (restrição compensável).** Evidência: `bin/forge-check:4471` só usa `regra_testes` e `regra_testes_enfraquecidos`, que somam `tests/` inteiro. Caminho: na 3ª volta, o autor tira a asserção que incomoda e compensa com uma asserção vazia em outro teste. A restrição do dono ("sem enfraquecer teste") passa calada (S4). Os portões ainda leem o diff da volta, por isso é recomendado. Correção mínima: somar `catraca.regra_controles_enfraquecidos(raiz, de, head)` e uma medida por função (asserções de cada `test_*` existente em `de` não podem cair), recusando a queda em qualquer função. Esforço: P a M. Dono: tech-lead. Pela regra, o recomendado de segurança volta e é corrigido antes do merge.

Observação, sem achado (não provada): `inicio` é o `Desde` da volta. Se a volta mesclar a develop e a develop tiver removido testes legítimos de outro item, a 3ª volta pode ser recusada por algo que não fez (falso positivo, falha fechada). Vale conferir ao corrigir o A3: medir só os arquivos que a volta mudou, ou descontar o que veio da base.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O afrouxamento do teto (1 para 3) tem a ORDEM DO DONO de 25/11 07:31; o rótulo `afrouxa-regra` é ato do dono e não deste parecer. Ferramentas: leitura do diff, os testes dos módulos tocados, `bin/forge-mutante` e sondas locais. Faltam no ambiente: gitleaks, semgrep, zizmor, actionlint e osv-scanner (lacuna). O diff não traz workflow nem dependência e, lido à mão, não tem segredo.
