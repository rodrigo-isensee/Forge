---
tipo: revisao-seguranca
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 6634cd800fd9366b1e8fcaf75e01e948e758880c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: F4-ATUALIZAR (revalidação 2, por delta)

Escopo: delta `4d86f26..6634cd8` (commits `106cb84` testes e `6634cd8` correção, volta 2) sobre o parecer anterior (`commit: 4d86f26`, reprovado por A4). `forge-check delta --parecer` lista `bin/forge-atualizar` (linhas 62-68, 115-126, 134-139), `changelog.d/f4-atualizar.md:2` e `tests/test_atualizar.py:495-525`. Reli tudo isso e também a função `resolver_conflito` inteira (linhas 126-153) e os chamadores (linha 273 e o `main`, linha 300). Revisão estática e sondas locais em repositórios descartáveis (`HOME` e `TMPDIR` em `$TMPDIR/security-engineer-f4`), sem rede externa.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `.forge/versao`, que só o dono altera, pelo terminal (`R-CONFORMIDADE`); e a `main` local, que é do usuário (`R-MAIN`).

## Achados
- A4 resolvido (S9 rodada de novo: `0.4`, `lixo` e `1.0.0-rc1` na develop, sem Traceback, sem `UU`, sem `MERGE_HEAD`, sem marcadores; aviso de formato X.Y.Z e a pergunta ao dono)
- A1 a A3 continuam resolvidos (o delta não toca nas linhas deles)

## Detalhe dos achados
**A4. Versão malformada derrubava o comando no meio da mesclagem (classe: conformidade, `R-CONFORMIDADE`, integridade de `.forge/versao`): resolvido.** A correção tem duas camadas. Em `bin/forge-atualizar:134-139`, a comparação só roda quando as duas versões são válidas. Se uma delas não for, aparece o aviso "não dá para comparar" e a pergunta continua com o padrão N. Em `bin/forge-atualizar:115-123`, `integrar_develop` envolve `resolver_conflito`: `EOFError`/`KeyboardInterrupt` fazem `merge --abort` antes de repassar a exceção ao `main` (que já as captura na linha 300), e qualquer outra exceção faz `merge --abort`, avisa e devolve False (cai no `oferecer_voltar`). Sonda S9, repetida com a harness da suíte:
- `0.4`, resposta n: `rc=1`, sem Traceback, aviso X.Y.Z, `status=[]`, sem `MERGE_HEAD`, `HEAD:.forge/versao=9.9.0`, sem marcadores.
- `lixo`, resposta n: igual.
- `1.0.0-rc1`, resposta n: igual.
- `0.4`, resposta s: `rc=0`, `.forge/versao=9.9.0`, árvore limpa. É o dono que escolhe, no terminal.

O teste `test_versao_da_develop_fora_do_formato_avisa_pergunta_e_com_n_desfaz_tudo` cobre `0.4` e `lixo`.

**A correção abriu outro caminho para mexer em `.forge/versao` sem o dono? Não.**
- O `.forge/versao` só é gravado em `checkout --ours` + `add` + `commit`, e só depois de `fv.confirmar` devolver verdadeiro. A pergunta continua atrás dos portões do `main` (`recusar_dentro_do_claude` e `tem_terminal`).
- O `except Exception` só desfaz: nunca conclui a mesclagem.
- O EOF no meio da pergunta, que antes deixava a mesclagem aberta, agora também desfaz.
- O aviso da develop local à frente do remoto (`bin/forge-atualizar:62-68`) só lê (`rev-list --count`) e imprime. Ele não mexe na develop local, e o teste da linha 513 confere que ela fica intacta.

Informativo, sem achado: se uma exceção surgir depois de um `commit` bem-sucedido (em `trazidos`, que só roda `git diff` e `print`), o `merge --abort` não faz nada e a mensagem "Desfiz a mesclagem" fica imprecisa. O commit nesse caso é o que o dono acabou de aprovar. Não há caminho realista e nada muda sem a resposta dele.

**Recomendados A7 e A8 (do review):** o delta do changelog (`changelog.d/f4-atualizar.md:2`) passa a descrever o merge local, a lista de arquivos trazidos, o padrão N e o desfazer em caso de erro. Bate com o código, e isso também é o que a A3 pedia. Nada novo pelo lado da segurança.

**Sondas e testes:** `s9.py` no scratchpad da sessão (4 casos, saída acima). `python3 -m unittest tests.test_atualizar`: 73 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: revisão manual, `forge-check delta` e sondas com git e python3 locais. Lacuna: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH. O delta não mexe em workflow nem em dependência, e não há nenhum segredo à vista no diff.
