---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae7-2-familias
commit: 62d27eb6ca7c576d9040e5ee7f230ba192798a58
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E107.7, revalidação do AE7.2 famílias geradas e alvo entrega)

Volta por delta (R-REVIEW): lido `forge-check parecer delta docs/security/v0480-ae7-2-familias.md`, intervalo `cb2043bc..62d27eb6` sem o que veio da develop; no domínio só `bin/forge_comparar.py` (commit 62d27eb6). A rodada anterior (E107.3, reprovado no cb2043bc) fica no git.

Gatilhos: controle de conformidade (comparador do "só aperta"), execução de código da árvore medida (gerador e forge-check do head).

## Estado dos achados anteriores
- A1 (bloqueante) resolvido: `bin/forge_comparar.py:423` passa a `cobertura` inteira por `ctx["seguro"]` (`sem_controle`, Cc, Cf, Zl e Zp viram espaço). Teste `FamiliasGeradas.test_id_gerado_com_quebra_de_linha_nao_forja_linha_da_saida`; sonda S1 refeita abaixo, com variantes.
- A2 (recomendado) resolvido: `bin/forge_comparar.py:57,90-113`, saída do gerador num arquivo anônimo com `RLIMIT_FSIZE` de TETO_GERADOS+1 (4 MiB) no filho, `fstat` antes de ler (nada inteiro à memória acima do teto), teto de 2000 linhas, stderr descartado; excesso, sinal SIGXFSZ ou rc diferente de 0 dão None (`nao-verificavel`). Testes de teto exato, de gerador que engole o erro da escrita e de teto de casos.
- A3 (recomendado) resolvido: `bin/forge_comparar.py:350-356`, HOME e TMPDIR criados por caso dentro do laço. Teste `AlvoEntrega.test_cada_caso_tem_home_e_tmpdir_proprios`.

## Sondas
- S1 · id gerado `gerada/x<SEP>so-aperta: medido base=FORJADO aceites-novos=0/01`, SEP = `\n`, `\r`, U+2028, U+0085, U+001E, hook LIBERA · espera: só a 1ª linha com `so-aperta:` · obtido: nas 5, rc 1 e o texto forjado dentro da linha `familias:`

## Conferido sem achado
O `RLIMIT_FSIZE` é herdado pelos netos do gerador; com a saída num arquivo e não num pipe, um neto que sobrevive ao prazo não trava mais o `subprocess.run`. Como root o gerador poderia subir o limite rígido, mas o `fstat` ainda recusa a saída acima do teto antes de ler, e o gerador já é código arbitrário do head com os poderes do usuário (modelo aceito no AE7.2), então não há ganho novo de atacante.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado: `python3 -m unittest tests.test_comparar.FamiliasGeradas tests.test_comparar.AlvoEntrega tests.test_comparar.CasoDoE50` (23 testes, OK) e a sonda S1 com as variantes. Suíte inteira: não rodada (brief E107.7, sem suíte local); o CI do PR a roda.
