---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i1-conserto
commit: b96357e9cdaa807422be47d586676cbbcf7e0612
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp2-i1-conserto (BP2 I1, `forge-fechar --conserto`, E38.6, revalidação)

Volta por delta. A rodada anterior (reprovada no head d816262d, A1 bloqueante e A2 recomendado no C4) fica no git (71a5d0ad). Delta lido: `forge-check parecer delta docs/security/v0479-bp2-i1-conserto.md`, intervalo `d816262d..b96357e9`; no domínio, `bin/forge-fechar` (só `conserto_c4`, linhas 1079-1121) e `tests/test_fechar.py` (classe `Conserto`: `base_com_os_testes` e os quatro testes novos do C4); fora do domínio, lidos por inteiro por serem a prova da correção: `tests/mutantes/fechar-conserto-7.json` (CS45 a CS49) e o fragmento do changelog. O resto de `bin/forge-fechar` não mudou no intervalo e vale a leitura anterior. Para avaliar o caminho SP4, li também `scripts/arvore-testada.py:60-74` e `tests/catraca.py:1720-1740` (sem mudança no intervalo).

## Gatilhos
Gatilhos: controle do Forge (portão de merge na develop), afrouxa-regra (R-FLUXO, decisão D5 do dono), CI e fluxo de branches.

## Estado dos achados da rodada anterior
- A1 (bloqueante): **corrigido.** `bin/forge-fechar:1110-1115` deriva a classe (`cls`) e o módulo (`mod`) do id e para também com `"setUpClass (cls)"`, `"tearDownClass (cls)"`, `"setUpModule (mod)"`, `"tearDownModule (mod)"` e `.ModuleSkipped.mod"`, todos com a aspa de fecho (um `test_bb` não casa com `test_b`). Prova: `tests/test_fechar.py:1631` (as cinco formas, por subteste), `:1639` (outra classe ou módulo segue, sem falso positivo), mutantes CS46 e CS47. A falha na própria classe (`ERROR: setUpClass (mod.C)` no run vermelho) vira a anotação `mod.C.setUpClass` (`scripts/falhas-no-resumo.py:132-134`, sonda local) e cai no mesmo laço.
- A2 (recomendado): **corrigido** como proposto. `bin/forge-fechar:1117-1118` exige `def <método>` como palavra inteira (`git grep -qwF`) no arquivo do módulo no `remoto_sha`; erro de leitura ou caminho errado também para (falha fechada). Prova: `tests/test_fechar.py:1644` (renomear `test_um` para `test_umdois` para), mutantes CS48 e CS49.
- Sonda S1 refeita no head novo: os três pulados reais gerados pelo carregador da stack (`setUpClass (test_m.C)`, `<carregador>.ModuleSkipped.test_n`, `setUpModule (test_o)`) contra o corpo do laço extraído de `bin/forge-fechar:1110-1114`: ids `test_m.C.test_a`, `test_n.K.test_c`, `test_o.E.test_e` deram "para" (antes: "segue"); `test_x.Z.test_q`, fora dos pulados, deu "segue". Rodei também os quatro testes novos do C4 (`Ran 4 tests`, `OK`).

## Caminho SP4 sem a checagem do teste apagado (escolha do autor)
**Aceitável, sem achado.** O `return 0` de `bin/forge-fechar:1105` (todos os passos "Testes do Forge (parte)" pulados) vem antes do laço, então nem os pulados nem o `git grep` rodam ali. Dois motivos tornam isso seguro hoje: (1) num PR `melhoria/*` → `develop`, que é o caso do `--conserto`, o SP4 nunca prova: `evento_elegivel` só aceita PR dos pares de `PROMOCOES` (`scripts/arvore-testada.py:68-71`, `tests/catraca.py:1720-1722`, todos com base `homolog` ou `main`), então as partes rodam a suíte e o C4 cai no laço completo; (2) se o SP4 provasse, a árvore do head seria a mesma, byte a byte, de um commit da develop com o job de prova verde: um teste "apagado" ali é a volta a uma árvore já verde (um revert), não uma falha escondida, e os pareceres do passo 1 veem o diff. Condição registrada (não achado): se um dia `PROMOCOES` ganhar um par com base `develop`, esse `return 0` precisa ser relido.

## Confirmação pedida pela D5 (por escrito)
**Preso ao commit revisado: confirmado** (trecho sem mudança no delta; linhas no head novo). O passo 2 exige o remoto igual ao `sha_conferido` (`bin/forge-fechar:1448`); o merge sai com `--match-head-commit "$remoto_sha"` (`bin/forge-fechar:830`, chamado na linha 1631); o C3 (`bin/forge-fechar:1069-1078`) só aceita o head M com `M^1` igual ao head conferido pelo pai (`FORGE_FECHAR_CONSERTO_H`, `bin/forge-fechar:900`), `M^2` igual ao topo do C1 e a árvore igual à do `merge-tree`.

**Com a mesma falha declarada: confirmado.** O C1 prende o run ao `push` na develop, ao topo lido do servidor e à conclusão `failure` (`bin/forge-fechar:1055-1060`), e o passo 6 relê o topo antes do merge (`bin/forge-fechar:1629-1630`). Com o A1 e o A2 corrigidos, o C4 só conta como passado no PR o teste anotado no run vermelho que o CI do PR rodou (não pulado pelo id, pela classe nem pelo módulo) e que segue no arquivo do módulo no head. A ressalva da rodada anterior cai.

## Achados

## Sondas

## Detalhe dos achados
Sem achado novo. Risco residual, não achado: o `git grep -w` acha `def <método>` em qualquer lugar do arquivo (um comentário, outra classe), então quem apaga o teste e deixa o texto num comentário passa o C4; é evasão deliberada, visível no diff que os pareceres do passo 1 leem, e o C4 não se propõe a provar que o corpo do teste segue o mesmo (esvaziar o teste também passa). A mudança do `sed` das anotações (o id vai até o primeiro espaço ou `:`) só estreita o id e não abre leitura nova: o texto continua passando só por `sed`, `awk` e `grep -F`.

## Riscos aceitos e ferramentas
Sem risco aceito. Os residuais da rodada anterior (janela entre a releitura do topo e o `--auto`; o C5 aceitar qualquer arquivo mudado desde o último verde, decisão D2 do dono) seguem como estavam.
Ferramentas: leitura estática, a sonda S1 local e os quatro testes novos do C4; o analisador de segredos, o de workflows e o lint de shell seguem fora do PATH desta estação (lacuna, sem instalação, `R-CUSTO`). Suíte: não rodada aqui (brief); o CI do PR no head b96357e9 é o portão dela.
