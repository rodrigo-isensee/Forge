---
tipo: review
contrato: 1
pedido: conf-correcao
branch: melhoria/conf-correcao
commit: 568757c630aec8d77111b54e84e1d564902ae92f
parecer: aprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-20
---
# Review do CONF-CORRECAO (E1.2, revalidação da volta 1)

Revalidação por delta (`agents/tech-lead.md`) sobre o parecer anterior (commit 13099560a326fc268c47cce68cc6a190678f855a, reprovado com A1 e A2). A revisão de segurança do código é da E1.3 (`docs/security/conf-correcao.md`); aqui não se refaz.

## Delta lido
`bin/forge-check delta --parecer docs/reviews/conf-correcao.md` → intervalo `13099560a326fc268c47cce68cc6a190678f855a..568757c630aec8d77111b54e84e1d564902ae92f`:
- `agents/conferente.md`:47
- `bin/forge-check`:2724, 2774, 2792-2793, 2914-2922, 2933-2936
- `tests/test_forge.py`:3279-3281, 3311-3320, 3453-3465

Já lido (parecer anterior, não relido): o resto da branch, isto é, E1 (`tardio:` e primeira passada), E2 fora das linhas acima, E3 fora das linhas acima, E4, `agents/jarvis.md`, `docs/regras/R-BRIEF.md`, `changelog.d/conf-correcao.md`, `tests/apoio_versao_defasada.py` e o risco DECISAO-ANCORA. Os pareceres em `docs/reviews/` e `docs/security/` do intervalo não entram no review de código.

## A1 (resolvido)
- `recusa_do_campo` (bin/forge-check:2914) recusa `\n` e `\t` e reaproveita `recusa_do_texto`: Cc fora de `\n`/`\t` (inclui ESC, `\x7f` e U+0085, que é Cc), Cf, Zl, Zp e os delimitadores. O laço da linha 2933 aplica a recusa a `--pedido`, `--destino`, `--ref`, `--etapa`, `--arquivo`, `--anterior` e cada `--parecer`, antes de qualquer leitura, com rc 2. Isso fecha também a R1 anterior (`--etapa` e `--pedido` com Cf).
- O caso de quebra de linha em `--etapa` passou de "higienizado" para "recusado" (test_forge.py:3279). Isso aperta o controle e não afrouxa nada.
- Sondas com o brief real `docs/briefs/conf-correcao-tech-lead-5.md`: `--ref abc123` → rc 0 (`Ref: abc123`). `--ref` com ESC, U+202E, U+0085 ou U+2028 → rc 2, sem texto. `--pedido` com U+202E → rc 2.
- Vermelho antes do verde (cópia em `$TMPDIR` com o `bin/forge-check` de 1309956 e os testes de 568757c): `test_campo_de_cabecalho_com_controle_ou_formato_rc_2` falha em 12 subtestes, e `test_campos_do_cabecalho_ficam_em_uma_linha` também falha. Com o `bin/forge-check` de 568757c, `MensagemRecusada` e `DecisoesCobradas` passam (35 testes OK).

## A2 (resolvido)
- `TOKEN_DE_MD` (bin/forge-check:2724) captura `(arquivo, linha)`, e a linha 2792 imprime `"<arquivo>:<linha>"` quando a citação a traz. É o `<rel>:<linha>` da M2.2. O único outro uso do padrão é o da linha 2774, já adaptado à tupla.
- `agents/conferente.md`:47 manda ler a linha `<linha>` do arquivo impresso e diz que o formato `D-<ID> = <opção> (dono, ...)` escapa ao grep de `DECISÃO DO DONO`. Sem `<linha>`, manda o grep `DECISÃO DO DONO|^\W*D-[A-Z0-9-]+ *=` só nesse arquivo, e a decisão lida tem de estar no brief. A restrição de caminho (M3.3) continua.
- O teste `test_fonte_fora_da_regra_com_linha_citada_d_etapas_inst` reproduz o caso real e falha com o código de 1309956 (vermelho), e o teste ajustado na linha 3453 exige o `:55` e o `:7`. Conferido: `~/.forge-contrib/docs/migracao-2026-10-15.md:55` é de fato a linha `D-ETAPAS-INST = A`.

## Suposição do autor (localizador, não conteúdo)
Aceita. O comando só imprime `<arquivo>:<linha>`, e quem lê o conteúdo é o conferente (`agents/conferente.md`:47). A M2.2 pede o localizador e o "não verificável", não a leitura. Se o comando lesse arquivo fora de `docs/pedidos/`, abriria a superfície de leitura que a M2.1 e a M3.3 fecham. A decisão continua cobrada (pelo conferente, por leitura), então não afrouxa.

## Saída das ferramentas (sem refazer)
- Suíte do autor (E1.1 volta 1, Histórico do pedido): 1035 testes OK. Quem roda a suíte inteira de novo é o pre-push deste push. O autor declarou que rodou com outra suíte em curso (desvio de R-TETO, já registrado no pedido).
- `.githooks/pre-push --status` antes do push → `nenhuma suíte do Forge rodando`, rc 1.

## Achados

## Recomendações (não bloqueiam)
- R6 · tests/test_forge.py:3312 · o teste novo não exercita `--pedido` nem `--parecer` com Cf. O código recusa (sonda: rc 2), mas falta a trava de regressão. Acrescente os dois ao laço.
- R7 · agents/conferente.md:47 · se o registro mudar e a `<linha>` citada ficar velha, a leitura cai em outra linha. Vale mandar o conferente usar o grep de fallback quando a linha lida não for uma decisão.
- R2 a R5 do parecer anterior continuam como estavam (R3 com a E1.3, R5 com o corpo do PR da E1.5).
