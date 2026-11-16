---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mutantes-velhos
commit: b79209008476123774e0e44338f17a467c8be699
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.202, item E2.196, mutantes velhos)

Parecer completo (não havia parecer anterior nesta branch), sobre o head b7920900, base 4138445e. Instância que não fez a entrega (classe T).

## Escopo lido
- Diff: 5 specs em `tests/mutantes/` e o fragmento `changelog.d/v047-mutantes-velhos.md` (24+/22-). Só dado de teste e `.md`: fora da conta do teto M14.
- Pedido E2.196: hooks-corpus-rapido M2-M5, lote-m8-mapa M2, lote-unico-032-l36 M7, maq-a7-medida M1-M6 e M15, v0441-o2-convencao M5. A entrega também alinha hooks-corpus-rapido M6, cujo `de` também não existia na base (`tests/apoio_volta_unica.py:428` já usa `getattr(modulo, marcador)`); mesma classe AR-12, declarado no fragmento. Aceito.
- O Forge não tem `docs/engineering/praticas.md`; o review segue o checklist da skill `engineering-practices` e `docs/engineering/achados-recorrentes.md` (PA-7).

## Verificação
- Cada `de` das 5 specs ocorre exatamente uma vez no arquivo declarado (contagem por script, 34 mutantes).
- `bin/forge-mutante --conferir --base 4138445e`: "conferidas: o trecho de cada spec do diff está no lugar".
- `bin/forge-mutante --processos 1` em cada spec (uma por vez; juntas a ferramenta recusa por serem de pedidos diferentes): 34 de 34 morreram, inclusive todos os alterados (hooks-corpus-rapido M2-M6, lote-m8-mapa M2, lote-unico-032-l36 M7, maq-a7-medida M1-M6 e M15, v0441-o2-convencao M5).
- Semântica preservada: cada `para` novo continua tirando a mesma guarda descrita em `guarda` (VOLTA_UNICA fora da regra, `test_comportamento` fora do mapa do forge-check, `modulos_da_convencao` fora do plano, CRITICO trocado por `None`); maq-a7-medida aponta para `bin/forge_apoio_testes.py`, onde o código foi parar.
- Suíte inteira: fica para o CI do PR (não rerrodada aqui).
- AR-12 (spec desatualizada): é o próprio objeto do item; conferido acima. AR-1 a AR-13 restantes não alcançam o diff (sem código nem teste novo).
- Commit único, Conventional Commits em português, mensagem clara.

## Achados

## Sondas

## Parecer
Aprovado. As specs listadas no E2.196 voltam a achar o trecho na fonte atual e todos os mutantes morrem no head b7920900; nada fora do escopo além do M6, que é a mesma correção. Fora do item (não bloqueia, vai como melhoria): uma varredura de `tests/mutantes/*.json` no mesmo head acha 246 mutantes com `de` ausente na fonte (por exemplo `tests/mutantes/conferente-c1.json` C1), ou seja, a classe AR-12 segue aberta além deste lote.
