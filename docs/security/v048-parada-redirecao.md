---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-parada-redirecao
commit: 101050172f9ce1e6717263a826cde736e4117917
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (parada, HOOK-PARADA-CONTA-REDIRECAO, E12.3)

1ª rodada completa no head 10105017 (E12.7), em paralelo ao review (E12.5) e ao QA (E12.6). Escopo: `hooks/vigia.py:68` (`_DESCARTE`) e `:169` (aplicação antes de `shlex`, alvo e verbos), `tests/test_vigia_descarte.py`, o fixture `tests/hooks/vigia/descarte-dev-null-nao-conta.json` e os mutantes M1-M4.

## Gatilhos
Gatilhos: hook de controle (aviso de contorno do vigia, R-CONFORMIDADE e R-MAIN), classe C por teste de controle.

## Resultado
Aprovado. O vigia é controle detectivo (aviso depois da chamada aceita), não barreira; o ator é o próprio agente refazendo por outra grafia o que o hook barrou. Comparei a mesma bateria de 29 sondas no código da base (`d056c2ca`) e no head: nenhuma escrita real no alvo barrado que a base acusava passa a escapar pelas grafias pedidas no brief.

- Colada a outra palavra (`x>/dev/null`, `>/dev/null'.git/config'`, `>/dev/null.git/config`, `>/dev/null>.git/config`, `2>/dev/null>.git/config`): a regex não casa (lookbehind e lookahead), o `>` segue em `verbos`; mesmo resultado da base.
- Aspas (`>"/dev/null"`): não casa, segue contando (conservador).
- Subshell e grupo (`(cat .git/config 2>/dev/null)`, `(echo x >/dev/null) > .git/config`, `{ echo x; } >/dev/null; echo > .git/config`): só o descarte sai; a escrita no alvo segue acusada.
- `&>>/dev/null`: casa e sai, correto (é descarte). `>|/dev/null` e `>&/dev/null`: não casam, seguem contando (conservador).
- Duas redireções (`>/dev/null >.git/config`, `> /dev/null > .git/config`, `2>/dev/null|tee .git/config`, `exec 3>.git/config 2>/dev/null`): o descarte sai, a outra fica.
- Orçamento: `_DESCARTE.sub` em entradas de 150 a 200 mil caracteres (dígitos, `>` seguido de brancos, `2>` e `&>` repetidos) leva até 0,07 s; o lookbehind de largura fixa deixa a varredura linear.
- Os True→False entre base e head são os pretendidos (ler o alvo com `2>/dev/null`; `/dev/null` deixa de ser alvo comum) e os dois furos de grafia dos cartões abaixo.

Suíte e testes: rodei `tests.test_vigia_descarte` no head (5 testes, OK). A suíte inteira fica para o CI do PR #962 (PQ-3 no relatório). Os mutantes M1-M4 cobrem a aplicação, o lookahead, o lookbehind e o `>>`; nenhum cobre a classe `\s` (cartão C1).

## Achados

## Sondas

## Detalhe dos achados
Sem bloqueante e sem recomendado que volte: pela ordem do dono citada no brief, furo de grafia no controle vira cartão, não volta. Os dois abaixo são de severidade baixa.

## Plano em cartões
- C1 (baixa, dono `tech-lead`, esforço P) · `hooks/vigia.py:68`: o `\s` do lookbehind e do lookahead é Unicode em `str` e casa `\xa0` (NBSP), `\x0b`, `\x0c`, ` `, que o shell não trata como separador. Sonda (programática, `perfil_da_chamada` + `eh_contorno` contra Write barrado em `/r/.git/config`): `echo x >/dev/null\xa0/../../r/.git/config .git/config` · base: verbos `['>']`, contorno True · head: verbos `[]`, contorno False. O shell grava pelo caminho `/dev/null\xa0/../../r/.git/config` (confirmado no scratchpad com `d\xa0/../alvo`), o que exige um diretório `/dev/null\xa0`, fora da área gravável do sandbox: caminho realista fraco. Correção mínima: `re.compile(..., re.ASCII)` ou trocar `\s` pelas classes explícitas `[ \t\n;&|(]` (lookbehind) e `[ \t\n;&|)]` (lookahead), com um subteste NBSP e um mutante que troque a classe de volta.
- C2 (baixa, dono `tech-lead`, esforço M) · `hooks/vigia.py:200`: Bash barrado e Bash aceito no mesmo alvo com os mesmos `verbos` é tido como correção. A base acusava por acaso `cp b .git/config 2>/dev/null` depois de `cp a .git/config` barrado (o `>` deixava os verbos diferentes); o head não acusa. É o ponto cego já existente da regra (na base, `cp b .git/config; true` também passa), não classe nova. Correção: comparar o comando normalizado (sem o descarte) ou os argumentos, além dos verbos.
- C3 (não é de segurança, ao `tech-lead`) · `hooks/vigia.py:360`: `grava_registro` aplica `_ESCRITA` ao comando cru, sem `_DESCARTE`; ler `docs/pedidos/` com `2>/dev/null` conta como gravação do registro (falso positivo, conservador). Consistência opcional.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varredura estática e sondas locais (biblioteca padrão), sem rede. Ausentes no PATH, registradas como lacuna: o varredor de segredos, o SAST, o auditor de dependências, os linters de workflow e o varredor de imagens; o diff não toca dependência, workflow nem segredo.
