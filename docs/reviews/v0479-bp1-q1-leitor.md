---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: df0251cab7badbc83f17f494a457bad66e2f263f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.44, BP1 Q1 formato e leitor puro da quarentena)

## Achados
- A2 (recomendado) bin/forge_quarentena.py:1 · a docstring e o fragmento `changelog.d/v0479-bp1-q1-leitor.md` citam `docs/propostas/v0479-bp1-quarentena.md`, que segue fora desta branch e da `develop` (só em `melhoria/v0479-estabilidade-bp`); o link fica quebrado se esta entrar antes. Vira cartão depois do merge.

## Sondas
- S1 · validar e ativas com {desde: 2030-01-01, prazo: 2030-01-08, autorizacao: A-1} e hoje 2026-11-21 · espera: erro de prazo ou entrada fora de ativas · obtido: validar ["`desde` no futuro (2030-01-01 depois de 2026-11-21)"] e ativas vazia

## Parecer
Aprovado no head df0251ca. Revalidação pelo delta: li só `forge-check parecer delta docs/reviews/v0479-bp1-q1-leitor.md`, intervalo d0619ab2..df0251ca (base atualizada de 004ce86 para 8a50379), domínio: `bin/forge_quarentena.py`, `changelog.d/v0479-bp1-q1-leitor.md`, `tests/mutantes/v0479-bp1-q1-leitor-4.json`, `tests/test_forge_quarentena.py`.

1. A1 (bloqueante no head d0619ab2) fechado: `_erros_da_entrada` recebe `hoje` e acusa `desde` no futuro (bin/forge_quarentena.py:76); com erro, `ativas` falha fechada e devolve vazio. Teste do ramo de falha `Validar.test_desde_no_futuro_e_erro` (borda: desde = hoje passa, hoje + 1 falha) e mutante Q22. A sonda S1 refeita no head novo dá o erro esperado.
2. Resto do delta (correções da segurança): leitura sem seguir link (`O_NOFOLLOW`), teto de 64 KiB lido com `read(TETO_BYTES + 1)`, chave repetida em qualquer nível por `object_pairs_hook`, `teste` restrito ao id de um teste só (regex ASCII com `fullmatch`) e teste repetido. Guardas curtas, cada uma com teste de comportamento do ramo de falha e mutante declarado (Q18 a Q23). Mérito de segurança é do parecer da segurança; aqui só leitura de código.
3. Tamanho: 118 linhas de código em `bin/forge_quarentena.py` contra a base, dentro do teto H1, um comportamento só.
4. Testes: `python3 -m unittest tests.test_forge_quarentena` 26 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-bp1-q1-leitor-4.json`: Q18 a Q23 morreram (6 de 6). `--cobertura --base d0619ab2`: as guardas novas das linhas 28, 38, 67, 76 e 101 cobertas.
5. Suíte inteira: fica no CI do PR (não rerrodada aqui).
6. Commit da correção: um, Conventional Commits em português, coerente.
