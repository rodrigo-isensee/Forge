---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: b0ffec816f8306b84660a00ae226317464ceed17
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E1.2 (guardas da conformidade no clone)

Escopo lido: `git diff 4182a6b9..b0ffec81` (hooks/conformidade.py, docstring de hooks/agentes.py, 6 fixtures, 2 specs de mutantes, tests/test_conformidade_verde.py, fragmento do changelog, índice de fixtures). Cartões: AGENTES-JSON-SEM-GUARDA e a parte de hook do CONFIG-TETO-SEM-GUARDA, contra C9, C10, C12 e C13 de `docs/security/v047-v2-ameacas.md`.

## Achados
- A1 (recomendado) docs/hooks.md:73 · O contrato ainda diz que a pasta de estado do clone "no Forge não tem guarda de escrita"; depois deste item é o contrário, e o config da raiz também ganhou guarda. Atualize o parágrafo na mesma entrega (definição de pronto).
- A2 (recomendado) tests/test_conformidade_verde.py:311 · O comentário diz "J1 a J11", mas o J10 (`chmod 000`) não está na lista e passa com rc 0 (minha sonda e S8 da segurança, A2 dela). Ao fechar o A2 da segurança, ponha o J10 no teste; até lá, o comentário não deve afirmar a cobertura.

## Sondas

## Aperta ou afrouxa
Aperta. A `GuardaDaProva` só ganha um ramo novo de `barrar` (a recusa cujo motivo é de `.git/forge/` ou de `.forge/config.json`, só com `no_clone`); nenhuma recusa que valia antes deixa de valer. O `caminho_barrado` sobrescrito só devolve `None` para a recusa do config fora da raiz da sessão, que na base também não valia no clone (a `GuardaDaProva` ignorava toda recusa fora da prova e da profundidade). O ajuste do padrão (`\.git/forge(?![\w.-])`) não libera nada: a linha com a prova da suíte continua com rc 2, agora pela recusa própria (R-VERIFY), e o M14 prova a troca. A mudança de comportamento é a rota manual: o jarvis deixa de editar o `agentes.json` (e o `.forge/config.json` da raiz). Isso tira poder, sem abrir exceção, logo é aperto; mas é a C12/R3 do modelo de ameaças, que pede decisão do dono antes do merge e registro no corpo do PR (`R-DECISAO`). O pedido tem 0 linhas DECISÃO DO DONO: pendência do jarvis para o merge, não do código. A C13 está cumprida (TRAVA-AGENTE-MORTO já na base, docs/hooks.md:73).

## Verificação
- Testes novos: `python3 -m unittest tests.test_conformidade_verde.EstadoDoAgentesNoClone tests.test_conformidade_verde.ConfigDoTetoNoClone`: 9 testes, OK.
- Mutantes: `bin/forge-mutante` nas duas specs, M1 a M14 (14 de 14) morreram; `--cobertura --base 4182a6b9`: toda condição mudada coberta.
- Sondas próprias (jarvis e qa-engineer, clone temporário): `./`, `docs/..`, `//`, link para a raiz, `mv .forge`, `cp`, `touch`, `$(git rev-parse --git-path forge/run)` recusam com rc 2; `cat` e `echo x > .git/forgery` liberam; `chmod 000 .git/forge/run/agentes.json` dá rc 0 (A2).
- Tamanho (H1): cerca de 48 linhas de código em hooks/conformidade.py, dentro do teto.
- Suíte inteira: não rodada (brief: sem suíte local); sem PR, CI do head não citável.

## Parecer
Aprovado no código: faz o que os dois cartões pedem pela via mínima da C9 (a `GuardaDaProva` deixa valer a recusa da política, sem regra nova), com teste de comportamento do ramo de falha e mutante por guarda, todos mortos. Os dois achados são recomendados. O item não está pronto para merge: o parecer de segurança no mesmo head (c56ae709) está reprovado com A1 (config lido da worktree, não da raiz da sessão) e A2 (`find -delete`, `tar -C`, `chmod`), que eu não repito aqui; a volta deles muda o patch, e este parecer revalida pelo `forge-check parecer delta`. Antes do merge, o jarvis leva a C12 ao dono.
