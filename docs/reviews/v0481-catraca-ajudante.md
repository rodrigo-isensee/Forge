---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-ajudante
commit: e05f8faab1b446658ee262461a6483829eae5c7b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.27, revalidação por delta do #891, catraca conta asserções de ajudantes)

Delta lido: `git diff ab293a4e..e05f8faa` (`forge-check parecer delta`: "revalida: sim", o parecer anterior barrou). Código: `tests/catraca.py` (+31/-12, 43 linhas mudadas; o item inteiro segue abaixo do teto H1), `tests/test_catraca.py` (3 testes novos, 2 ajustados), specs D3B5, D3C5, D3D2, D3H7, CA6 e CA7 realinhadas, `tests/mutantes/v0481-catraca-ajudante-3.json` (CA14-CA21) e o fragmento do changelog. Os pareceres de QA e de segurança entraram na branch no mesmo intervalo e não foram relidos aqui.

## Parecer
Aprovado. Os achados da rodada anterior estão resolvidos: A1 (specs D3 fora da fonte) e o A2 recomendado (a mensagem agora diz "perdeu asserção (estava no ajudante X)").

**Desvio do brief (estouro do teto conta só as asserções diretas, em vez de tornar o módulo ilegível): aceito.** Sondas próprias em `$TMPDIR` (`sonda_teto.py`, `sonda_ab.py`), rodando as catracas da base 220ba3fa, do ab293a4e e do head:
- **S-a.** Leque de 100 ajudantes × 100 chamadas nos dois lados, e o PR tira `self.assertEqual(self.r, 42)` do ajudante `alvo` de `T.test_y`. Base 220ba3fa: `[]`. Head: `[]` (1,97 s). ab293a4e: barraria (o leque desse tamanho termina em 3,8 s). O head só deixa passar calado o que a catraca da `develop` já deixava passar.
- **S-b.** O PR acrescenta o leque e tira a asserção no mesmo commit. Head: `perdeu asserção (estava no ajudante alvo)` e valor trocado. Quem estoura o teto só no lado novo barra, e a falha fica fechada.
- **S-c.** O PR tira o leque (sai do teto) e tira a asserção. Head: `[]`. A base 220ba3fa também dá `[]`.
- **S-d.** Nenhum dos 276 módulos de `tests/` do head estoura o teto. Hoje o caso S-a não existe na árvore.

Os dois caminhos calados exigem que o módulo já estoure o teto na base: pelo menos 2 milhões de expansões, o que só acontece com um leque gerado de propósito e mesclado antes com review. O ab293a4e barraria o S-a, mas esse commit nunca entrou na `develop`, e a referência do "nada que barra deixa de barrar" é a `develop`. Tratar o módulo como ilegível, como pedia a segurança (A1 dela), seria pior. Lido em `tests/catraca.py:806-810`: `_testes_por_modulo` descarta o módulo ilegível dos dois lados. No caso S-a, nenhum teste do módulo seria comparado, nem pelas asserções diretas. A docstring de `testes_da_arvore` (`:758-760`) registra o motivo.

O que mais conferi:
- **Teto.** `_gasta` debita os nós lidos e as chaves somadas num orçamento único por módulo, e a nova passagem com `fundo=0` e `math.inf` não chama ajudante nenhum. O teste de tempo usa a entrada da S9 da segurança, com folga de 10 s contra cerca de 1 s medido.
- **Mutantes (V2).** `bin/forge-mutante --processos 1`: CA14-CA21 morreram. CA6 morreu. CA7 morreu por erro do teste declarado, como na rodada anterior. D3B5, D3C5, D3D2 e D3H7 morreram nas linhas novas. `--cobertura --base ab293a4e`: as 4 condições novas (`:720`, `:752`, `:786`, `:787`) têm mutante declarado. `--conferir --todas` no head dá a mesma saída que em 220ba3fa (diff vazio), e `ConferirTodas` passa.
- **Testes tocados.** `AssercaoNoAjudante` e `TestesAfrouxados` (30 testes) passam no clone. Os novos fecham o A2 do QA: os argumentos posicional e nomeado e o corpo do ajudante viram valor trocado, e a cadeia `um`→`dois`→`tres` conta até o fim.
- **CI do #891 em e05f8faa** (run 45568861266). As 10 partes da suíte (3.12 e 3.14), a instalação, os passos, as verificações longas e o teto de pulados estão verdes. `bateria (pareceres)` e o agregado `bateria` esperam os pareceres neste head. `catraca` pede o rótulo `afrouxa-regra` do dono, porque o PR toca `tests/catraca.py` (ADR 0008); o rótulo fica com o dono depois do último push.

Leitura (checklist): a troca de `FUNDO_DOS_AJUDANTES` pelo literal 8 no teste antigo dá ao teste o poder de matar o mutante CA21. `math.inf` como orçamento no `_perfil_do_teste` avulso mantém os chamadores antigos sem teto. As mensagens e o fragmento do changelog descrevem o comportamento novo.
