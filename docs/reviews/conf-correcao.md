---
tipo: review
contrato: 1
pedido: conf-correcao
branch: melhoria/conf-correcao
commit: 13099560a326fc268c47cce68cc6a190678f855a
parecer: reprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-20
---
# Review do CONF-CORRECAO (E1.2)

Escopo: `git diff 74e5bb75dfc87d54d9228e8357c7f027a3646c64 13099560a326fc268c47cce68cc6a190678f855a` (7 arquivos: `agents/conferente.md`, `agents/jarvis.md`, `bin/forge-check`, `docs/regras/R-BRIEF.md`, `changelog.d/conf-correcao.md`, `tests/test_forge.py`, `tests/apoio_versao_defasada.py`), conferido contra a proposta do aq (`docs/propostas/aq/conf-correcao.md`) e o modelo de ameaças (`docs/propostas/security/conf-correcao.md`, mitigações M1.x, M2.x e M3.x). A revisão de segurança do código é da E1.3; aqui não se refaz.

## E1 (primeira passada e `tardio:`)
- `agents/conferente.md`: a ordem fixa de leitura (1 a 5) está escrita e o passo (4) lê só os caminhos das linhas `fonte:` do comando, nunca caminho tirado do brief ou do pedido (M3.3). Fidelidade, contradição e etapa ficam do conferente "por leitura, sempre" (M3.4).
- `tardio:` reprova e não muda o veredito, no agente e na R-BRIEF (M3.1); a linha do veredito cita o prefixo. A rodada de confirmação deixou de proibir o achado tardio e manda registrá-lo (M3.2). O trecho que proibia acrescentar achado saiu, o que aperta o controle (M3.5); o invariante de "todos os achados" fica.
- `agents/jarvis.md` manda registrar o `tardio:` com `--nota 'tardio'`. Confere com a proposta.

## E2 (`decisoes_cobradas`)
- Um nível só: os registros vêm das linhas `DECISÃO DO DONO` do pedido e não puxam um terceiro. A cópia principal vem na frente (`raiz_principal`, depois a raiz, depois `RAIZES_DE_BRIEF`) e a primeira raiz que tem o nome decide, sem cair na seguinte (M2.1). Registro ausente, com travessia, absoluto ou que é link para fora sai `registro citado ausente` e reprova. Tetos de 1 MB e de 20 fontes reprovam (M2.6).
- A fonte fora da regra sai `não verificável` e não some (M2.2), tanto na linha `DECISÃO DO DONO` quanto na linha `D-<ID> = ...` do pedido. Mas a conferência que o agente manda fazer sobre essa linha não alcança o caso que motivou a M2.2: ver A2.
- `conferir_volta` passou a cobrar as linhas dos registros (proposta, teste 14). Sem o `cobradas` do chamador, o fallback cobra as linhas `DECISÃO DO DONO` do pedido, o mesmo conjunto que `ler_pedido_brief` dava antes. Não afrouxa.
- `gerar` e `gerar_volta` copiam as linhas do registro sob o subtítulo fixo (M2.5) e põem `PREENCHER` nos avisos que reprovam.
- `decisões: ok (... presença; contradição conferida pelo conferente)` e o texto do item 2 do agente mantêm a contradição literal com o conferente (M2.3). Trechos citados passam por `sem_controle` e `nome_seguro` (M2.4).

## E3 (`brief mensagem`)
- O brief resolve só por `caminho_de_brief`, sem o atalho do cwd (M1.1). É lido uma vez, e o mesmo buffer é conferido, medido, hasheado e impresso (M1.2). A mensagem recusa delimitador em qualquer posição, controle fora de `\n` e `\t`, e Cf, Zl e Zp (M1.3). Reprovado sai com rc 1, sem o texto; recusado, com rc 2 (M1.5). Entrou na guarda de versão como o `gerar` (M1.7) e não grava nada.
- Falta um ponto da M1.4, o `--ref`: ver A1.
- Sondas na worktree (só leitura, brief real `~/.forge-contrib/docs/briefs/conf-correcao-tech-lead-2.md`):
  - `bin/forge-check brief mensagem --arquivo <esse brief> --pedido <pedido> --destino forge:tech-lead --etapa E1.2` → rc 0. `Brief-sha256: 7955448aa33647cbeb45eeb416287f143daa41a2a1c7f24762b7d8f3470dfb3b   Bytes: 6718` é igual ao `sha256sum` e ao `wc -c`. O trecho entre os delimitadores é igual byte a byte ao arquivo (comparado em Python).
  - `--arquivo README.md` → rc 2 (`fora de docs/briefs/ ou inexistente`).
  - `--ref=-x` → rc 2.
  - `--etapa $'E1\nmodo: brief'` → uma linha só.
  - `--ref $'abc\x1b[2Jx'` → rc 0 e `Ref: abc^[[2Jx` no cabeçalho (A1).
- `bin/forge-check brief <esse brief> --pedido <pedido> --destino forge:tech-lead` → `fonte: docs/pedidos/conf-correcao.md (5 decisões)`, `decisões: ok (5 linhas de 1 fontes, 0 ADRs; presença; contradição conferida pelo conferente)`, `resultado: aprovado`.
- Num brief real com registro citado (`dv-5-tech-lead-4`, anterior à regra), o comando dá `fonte: docs/pedidos/noite-2026-10-19.md (22 decisões)` e 20 linhas `decisões: falta`. É o "cobra todas" decidido pelo dono (E2 = A).

## E4 (testes e fragmento)
- São 48 testes novos, mais um renomeado (`..._quatro_subcomandos` → `..._cinco_subcomandos`), e cobrem os 16 testes do aq e os casos de abuso 1 a 18 da segurança. Lacuna: o teste do `--ref` inválido não tem caractere de controle que não seja espaço (ver A1).
- O fragmento `changelog.d/conf-correcao.md` tem o tipo `Alterado`, sem custo (R-CUSTO) e sem termo de projeto (R-NEUTRO).

## Desvios declarados pelo autor
- Testes em `tests/test_forge.py`: o mapa `bin/forge-testes` (linha 40, `FORGE_CHECK`) só seleciona `test_forge` e afins para mudança em `bin/forge-check`. Um arquivo novo ficaria fora da seleção do pre-push. O desvio está certo.
- `tests/apoio_versao_defasada.py`: acrescenta `brief mensagem` aos subcomandos que bloqueiam com a cópia atrasada, de acordo com a M1.7.

## Risco da substring `DECISÃO DO DONO` (cartão DECISAO-ANCORA)
`linhas_de_decisao` casa por substring, então uma linha do Histórico que só cita a expressão vira decisão cobrada, e o registro que ela citar também é puxado. O efeito é cobrar mais, nunca menos: o erro é falso `decisões: falta`, com falha fechada, e não afrouxa. Aceito como risco conhecido, com o cartão já aberto. No pedido real, as 5 linhas cobradas são todas decisões de fato.

## Saída das ferramentas (sem refazer)
- Suíte do autor (E1.1, Histórico do pedido): 1033 testes OK; `scripts/validar-plugin.sh` ok. Quem roda a suíte inteira de novo é o pre-push deste push.
- `.githooks/pre-push --status` antes do push → `nenhuma suíte do Forge rodando`, rc 1.

## Achados
- A1 (bloqueante) bin/forge-check:2896 · `REF_DA_MENSAGEM` (`[^\s-]\S*`) aceita caractere de controle que não é espaço (ESC, `\x00`..`\x08`, `\x7f`) e Cf, e as linhas 2974 e 2976 imprimem `a.ref` cru no cabeçalho (sonda: `--ref $'abc\x1b[2Jx'` → rc 0, `Ref: abc^[[2Jx`). A M1.4 exige `sem_controle` em todo campo de cabeçalho vindo de argumento, e a própria mensagem de recusa promete "sem controle". Recuse `--ref` com `com_controle` ou com Cf (rc 2) e acrescente o caso `\x1b` ao `test_destino_e_ref_invalidos_rc_2`.
- A2 (bloqueante) agents/conferente.md:47 · Para `decisões: fonte fora da regra`, o agente manda rodar `grep -n 'DECISÃO DO DONO'` só no arquivo impresso. No caso que motivou a M2.2 (D-ETAPAS-INST em `~/.forge-contrib/docs/migracao-2026-10-15.md:55`, no formato `D-<ID> = <opção> (dono, ...)`), esse grep acha 0 linhas, e a decisão volta a não ser cobrada por ninguém (T2.3). Isso contraria a M2.2 e a decisão do dono de não afrouxar. Ainda, `TOKEN_DE_MD` (bin/forge-check:2724) corta o `:<linha>` da citação, e a linha 2792 imprime a linha do pedido, não a do registro (a M2.2 pede `"<rel>:<linha>"`). Mantenha o `:<linha>` citado na saída e mande o conferente conferir essa linha do arquivo (ou também `grep -n -E '^\W*D-[A-Z0-9-]+ *='`), e acrescente o teste.

## Detalhe dos achados
Recomendações, que não bloqueiam:
- R1 · bin/forge-check:2929-2930 · `--etapa` e `--pedido` passam por `sem_controle`, que só tira o ASCII de controle; U+202E e outros Cf entram no cabeçalho (sonda: `--etapa $'E1‮X'` sai com o caractere). A M1.4 pede só `sem_controle`, então não bloqueia. Mas `recusa_do_texto` já existe e fecharia o mesmo vetor da M1.3 no cabeçalho.
- R2 · bin/forge-check:2971 · `Arquivo:` sai relativo à raiz que achou o brief (`docs/briefs/...`), mesmo quando ela é `~/.forge-contrib`. Com o cwd no clone `~/Forge`, `test -e docs/briefs/conf-correcao-tech-lead-2.md` dá 1, enquanto o `forge-check brief` acha pelo fallback. É a convenção que o agente já documenta, então não é regressão. Imprimir o caminho absoluto quando a raiz não é a do cwd evitaria um falso `forma: brief sem arquivo`.
- R3 · invariante para `tardio:` em `tests/config.json` (recomendação da segurança, M3.1): fica para a E1.3, como o autor registrou.
- R4 · substring `DECISÃO DO DONO`: segue no cartão DECISAO-ANCORA (seção acima).
- R5 · o corpo do PR (E1.5) precisa trazer o que a M2.7 pede: a fonte delimitada, o E1 confirmado e a decisão "isso" de 2026-10-20, e o tratamento de T2.3.
