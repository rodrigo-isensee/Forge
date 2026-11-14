---
tipo: revisao-seguranca
contrato: 1
pedido: v047-heredocs-orcamento
branch: melhoria/v047-heredocs-orcamento
commit: ec8997a6bfb365a9061316ea7905d12e8d5279a7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-heredocs-orcamento

Intervalo `origin/develop..ec8997a6` (base `f4b0c2ae`), um commit: `menor_custo` em `tests/apoio_volta_unica.py`, `medir_o_hook` em `tests/test_hooks.py`, os testes de `menor_custo` em `tests/test_medida_cpu.py`, a ficha de mutantes e o fragmento do changelog. Nenhum hook, workflow ou código de produção muda.

## Gatilhos
`R-SEGURANCA`, pelo apoio de teste dos controles de orçamento do hook `conformidade` (achado A1 do LOTE-LEITURA-HOOK: hook que passa do timeout é liberado pelo Claude Code). A pergunta do portão: o `menor_custo` afrouxa o orçamento? Não, pelos motivos abaixo.

- **Limites iguais.** Conferido no diff: `1.0` s de CPU (2000 comandos lógicos), `3.0` s de CPU (heredocs), `limite / 2` (metade do timeout do `hooks.json`) nas três medidas da linha adversária e `PRAZO_DA_LINHA_S` (ou `limite / 2` sem `resource`) nos donos de heredoc. O `assertLess` segue estrito e igual ao corte do `menor_custo` (`<`; o mutante M2 prova).
- **Só a medida acima do limite se repete**, no máximo 3 vezes (M4), e vale a menor (M3). Custo de CPU sob carga só soma (troca de contexto, cache), então a menor medida estima o custo do código; regressão determinística acima do limite passa dele nas 3 e reprova (`test_regressao_passa_do_limite_nas_tres_e_para_na_terceira`).
- **A decisão é conferida em cada tentativa.** `medir_o_hook` chama `executar_fixture`, que confere código de saída e `stderr` a cada medida; uma tentativa com decisão errada derruba o teste, e a repetição não escolhe a "boa".
- **A linha adversária ficou mais estrita num ponto:** antes rodava com o prazo de relógio da linha de produção (3 s), e a recusa por esse prazo também traz `R-CONFORMIDADE`, então podia passar pelo relógio; agora, com `LANCADOR_SEM_PRAZO_DA_LINHA`, só passa se a regra ou os tetos de contagem e caracteres recusarem dentro do orçamento de CPU.
- O único efeito que não reprova é o estatístico: código cujo custo real fica rente ao limite passa um pouco mais vezes. É o objetivo declarado (TESTE-HEREDOCS-ORCAMENTO-ESTAVEL) e não muda o limite.

## Achados
- A1 (recomendado) tests/test_hooks.py:1122 · a linha adversária passou de relógio a CPU: um bloqueio sem CPU (espera de subprocesso ou trava) no caminho dela não reprova mais aqui; a parede só vai à mensagem. A garantia de relógio fica no vigia de decisão (test_t_vigia_*); vale um teto largo de parede (o timeout inteiro).

## Sondas

## Detalhe dos achados
**A1** · evidência: `tests/test_hooks.py:1122` (e as duas medidas seguintes, linhas 1133 e 1143), com `medir_o_hook` (`tests/test_hooks.py:986`) medindo `RUSAGE_CHILDREN` sob `LANCADOR_SEM_PRAZO_DA_LINHA`. Caminho de ataque: nenhum direto; é perda de cobertura. Uma mudança futura no `conformidade` que espere sem gastar CPU (por exemplo, uma chamada externa sem prazo) no caminho da linha adversária passaria neste teste e, em produção, só seria contida pelo vigia de `PRAZO_DA_DECISAO_S`, que recusa só com marcador crítico (`test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem`). O desenho de CPU com o vigia testado à parte já era o do teste dos donos de heredoc (P3 da 0.43.1), revisado antes; por isso não bloqueia. Severidade: baixa. Correção mínima: na linha adversária, além do `assertLess(custo, limite / 2)`, um `assertLess(parede, limite)` (o timeout inteiro do `hooks.json`, folga de 2x sobre o orçamento, que a carga comum não alcança). Esforço: P. Dono: `qa-engineer`.

Informativo: o `registrar_orcamento` dos donos de heredoc passa a registrar a menor medida de cada forma, não a única; o log do orçamento subestima um pouco o pior caso observado sob carga. Sem efeito no portão.

## Riscos aceitos e ferramentas
Sem risco aceito. Conferido: diff inteiro do intervalo; `bin/forge-mutante tests/mutantes/v047-heredocs-orcamento.json` (M1 a M4 morreram); `tests.test_medida_cpu` e `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento` rodados e verdes no clone. A suíte inteira é do CI do PR. Varreduras de segredo e de workflow não se aplicam (sem segredo nem workflow no diff); as ferramentas delas não estão no PATH deste ambiente (lacuna registrada).
