---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 9ec21d93d609fc49aa696f796236f59586529572
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E93.6, revalidação da FALA-DO-DONO-RESUMO-COMPACTADO)

Volta por delta sobre o parecer no head 06a0220a (a rodada anterior está no git). Base fb3b670b.

Gatilhos: hook de controle (classificador da fala do dono, que decide o aviso do vigia e a medida do meta).

## Delta lido
`forge-check parecer delta` de 06a0220a..9ec21d93: no domínio `hooks/vigia.py:302-312` (docstring e marca `is[A-Z]` com `re.match`) e as fixtures novas `tests/hooks/vigia/entrada-forma-da-ide-sem-origem-avisa.json` e `entrada-campo-issue-ref-nao-e-marca-avisa.json`. Fora do domínio: changelog, `docs/hooks-fixtures.md`, mutantes, `tests/test_vigia.py`.

## Achados anteriores
- A1 (recomendado) da rodada anterior: corrigido. A docstring em `hooks/vigia.py:305-306` diz que sem `origin` é a forma antiga e a atual da extensão de IDE (com `promptId`); a fixture da forma da IDE prova que ela segue como fala do dono.

## Detalhe
**`is[A-Z]` não deixa escapar marca real.** Chaves de topo que começam com `is` (sem diferenciar maiúscula) em 1.150.798 registros dos transcritos locais (só chaves, sem conteúdo): `isApiErrorMessage`, `isCompactSummary`, `isMeta`, `isSidechain`, `isSnapshotUpdate`, `isVisibleInTranscriptOnly`; todas casam com `is[A-Z]`. Nenhuma com dígito, `_` ou minúscula depois do `is`. O cliente grava campos em camelCase e é ele, não o modelo, quem grava as chaves do registro (fronteira já descrita na rodada anterior), então uma marca futura fora do padrão é hipótese sem caminho de ataque.

**Só aperta em relação à base.** Base, 06a0220a e 9ec21d93 lado a lado sobre os registros `user` do corpus local: base aceita 1406, 06a0220a e o novo aceitam 1341; aceitos pelo novo e recusados pela base: 0; diferença entre 06a0220a e o novo: 0 nos dois sentidos. Sondas sintéticas (chave verdadeira num registro com `origin` humano): `isMeta`, `isSidechain`, `isCompactSummary`, `isX`, `isQualquer` ficam fora no novo; `is_meta`, `is1`, `ismeta`, `is`, `is_`, `isÉ`, `isé`, `issueRef`, `isolado`, `IsMeta` passam no novo e passavam todas na base. Em relação a 06a0220a o novo afrouxa só essas formas, que não são marca do cliente (o fim do falso positivo de `issueRef` é o objetivo da mudança). Nenhuma forma que a base recusa o novo aceita.

**meta.py** segue herdando por `texto_do_dono` (`tests.test_meta` verde).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `tests.test_vigia` e `tests.test_meta` (44 testes, OK), comparação base×06a0220a×novo e sondas sobre os transcritos locais (só chaves). Suíte inteira: fica para o CI do PR (por brief). Ferramentas de SAST e varredura de segredos não estão no PATH: lacuna registrada.
