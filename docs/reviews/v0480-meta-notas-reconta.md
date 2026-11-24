---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas-reconta
commit: 25c6a8be55fd458c627fe3f28dd1ae6609483d9a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · marca das notas por transcrito e nota com tool_result na entrada, etapa E137.16 (PR #822)

Revisão completa do intervalo `0e59c446..c947a063` (3 commits): `hooks/meta.py` (+15 linhas de código, dentro do teto H1), `tests/test_meta.py`, `tests/mutantes/v0480-meta-notas-reconta.json`, `tests/mutantes/v0478-meta-notas-3.json` e o fragmento `changelog.d/v0480-meta-notas-reconta.md`. Revalidação por delta no head 25c6a8be (E137.25), abaixo.

## Ferramentas citadas
- `python3 -m unittest tests.test_meta` (ambiente limpo, no head): 54 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-meta-notas-reconta.json` (rev c947a0634110): M1, M2, M3 e M4 morreram.
- `bin/forge-mutante tests/mutantes/v0478-meta-notas-3.json` (rev c947a0634110): M15 a M22 morreram; M15, M20 e M21 foram reescritos para a forma nova e seguem mirando guarda viva.
- Suíte inteira: fica com o CI do PR #822 (check `catraca` pendente na leitura), sem rerrodar aqui.

## Leitura
- Marca por transcrito (A1 de `docs/reviews/v0480-meta-notas.md`): `vistas_anteriores` devolve `{transcrito: marca}` e descarta a entrada que não é objeto; `notas_em_outro_idioma` tira a do transcrito, mede e a recoloca no fim, então a ordem do dict é a do uso mais recente e o corte `[-MARCAS_GUARDADAS:]` tira a mais velha. O teste `test_stop_de_outra_sessao_no_meio_nao_faz_recontar` reproduz a sonda A, B, A do achado e dá 0 no 2º Stop de A.
- Pré-filtro: a linha só é pulada sem decodificar quando traz `"type":"tool_result"` e não traz `"type":"assistant"`. Na linha do resultado de ferramenta o texto é string com aspas escapadas, então o par do assistente não aparece ali por acaso. Se aparecer num `toolUseResult` em forma de objeto, o único efeito é custo: a linha decodificada tem conteúdo que não é só texto, `texto_do_dono` devolve None e o tipo não é `assistant`, então ela não para a rodada nem vira nota.
- Formato antigo do `notas.json` (`{"transcrito", "marca", "final"}`, valores string): todas as chaves saem pelo filtro `isinstance(v, dict)`, o 1º Stop depois da atualização reconta a rodada uma vez e regrava o arquivo na forma nova; o 2º Stop já não reconta (S1). É uma vez por projeto, sem erro nem perda da linha da medida. O fragmento do changelog não diz isso (A1).
- Corrida entre dois Stops quase simultâneos de sessões diferentes: quem grava por último pode apagar a marca da outra, que reconta uma vez. A gravação é atômica (`gravar_json` com `os.replace`), o arquivo não se corrompe e o caso é bem mais raro que a alternância que o item corrige; não é achado.
- Commits em Conventional Commits, com o pedido e a etapa; o fragmento traz custo e reversão (`R-DECISAO`).

## Revalidação por delta (head 25c6a8be, etapa E137.25)
- Delta lido: `forge-check parecer delta` no intervalo `c947a063..25c6a8be`, sem o que veio da `develop` (merge 2da8dd51). No domínio, só `tests/mutantes/v0478-meta-notas-2.json` (M10) e `tests/mutantes/v0478-meta-notas.json` (M1); `tests/test_meta.py` e `tests/mutantes/v0480-meta-notas-reconta.json` dispensados (teste do QA aprovado em 6b1b7c1).
- Só o `de` muda, para o texto atual de `hooks/meta.py:285-286` (cada trecho ocorre uma vez no arquivo); `hooks/meta.py` não muda no delta. O `para` segue mirando a mesma guarda: M10 troca o pulo do `tool_result` por `False` (a linha volta a ser decodificada) e M1 troca o `and` do filtro user/assistant por `or`. Testes que matam cada um, os mesmos.
- `bin/forge-mutante --ids M10 tests/mutantes/v0478-meta-notas-2.json` (rev 25c6a8be55fd): `M10 · morreu · hooks/meta.py:285`.
- `bin/forge-mutante --ids M1 tests/mutantes/v0478-meta-notas.json` (rev 25c6a8be55fd): `M1 · morreu · hooks/meta.py:286`.
- `bin/forge-mutante --conferir --base c947a063`: "conferidas: o trecho de cada spec do diff está no lugar".
- CI do #822 no head, na leitura: partes da suíte pendentes, `catraca` verde, `bateria (pareceres)` vermelha com o parecer ainda em c947a063 (este commit o atualiza); sem rerrodar aqui.

## Achados
- A1 (recomendado) changelog.d/v0480-meta-notas-reconta.md:2 · O notas.json na forma antiga (marca única) vira {} na forma nova: o 1º Stop de cada projeto depois da atualização reconta a rodada uma vez (S1). Dizer isso no fragmento, para quem ler a medida notas_em_outro_idioma da versão.

## Sondas
- S1 · notas.json antigo `{"transcrito": <t.jsonl>, "marca": "u2", "final": sha256(PT)}` e a rodada dono u0, nota EN u1, final PT u2, medida duas vezes · espera: 1º Stop (1, True), arquivo só com a chave do transcrito, 2º Stop (0, False) · obtido: (1, True), [t.jsonl], (0, False)

## Parecer
Aprovado. A marca por transcrito resolve a reconta entre sessões, o pré-filtro deixa de pular a nota cuja entrada traz o par `"type":"tool_result"` e os mutantes das duas specs morrem. O efeito do formato antigo é uma reconta única, aceitável; a nota no changelog (A1) fica como recomendação, sem devolver. No head 25c6a8be, M10 e M1 realinhados ao pré-filtro atual morrem na mesma guarda; lógica igual.
