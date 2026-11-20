---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-medida-afirmacao
commit: f15b9b85e5c42f9310f7523fc2c25c5a35b8d3b4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E58.20 (AE1.4, medida da afirmação sem prova)

Diff revisado: `ed5bfa02..f15b9b85` (1 commit; `hooks/meta.py`, `agents/jarvis.md`, `tests/test_meta.py`, `tests/mutantes/v0479-ae1-medida-afirmacao.json`, `changelog.d/v0479-ae1-medida-afirmacao.md`). Código de produção: 15 linhas em `hooks/meta.py` (H1 dentro do teto).

## Ferramenta (citada, sem refazer)
- `bin/forge-mutante tests/mutantes/v0479-ae1-medida-afirmacao.json --processos 1` (rev f15b9b85e5c4): M1 a M6 morreram (`hooks/meta.py:240`, `:241`, `:246`).
- Teste novo: `python3 -m unittest tests.test_meta.AfirmacaoSemProva`, 4 testes, OK. Suíte inteira: fica com o CI do PR (`R-REVIEW`).

## Leitura
- Requisito: o desenho aceito pelo dono (`docs/propostas/v0479-melhorias-anti-erro.md:147`, linha do AE1.4) manda contar a afirmação no texto **fora** da citação e do código ("conta o texto fora dos dois"). O código conta o texto inteiro (`hooks/meta.py:238-246`), e o teste `test_afirmacao_escondida_em_citacao_ou_codigo_tambem_conta` (`tests/test_meta.py:509`) fixa o contrário do desenho. O desvio veio do brief do autor (erro do Jarvis, não do autor); vale o desenho.
- O que muda:
  1. `hooks/meta.py:246`: a afirmação é procurada em `fora_de_codigo_e_citacao(texto)` (o leitor que já serve ao jargão e ao idioma, linha 177); a linha `onde:` continua procurada no texto inteiro, porque a saída colada vem em bloco de código ou citação.
  2. `hooks/meta.py:238-239` (comentário) e `changelog.d/v0479-ae1-medida-afirmacao.md` ("também em citação ou código"): passam a dizer que citação e bloco de código não contam.
  3. `tests/test_meta.py:509`: o teste inverte (`> mesclado` e bloco cercado com `integrado` dão `False`; uma afirmação fora, com outra dentro da citação, segue `True`). O caso de código em linha (`` Está `feito`. ``) segue o leitor existente, que só tira bloco cercado: fica `True`, e o teste deve dizer isso.
  4. Mutante novo para a guarda nova (trocar `fora_de_codigo_e_citacao(texto)` por `texto` deve morrer pelo teste invertido).
- `agents/jarvis.md`: a frase nova ("feito, mesclado ou integrado, com a linha `onde:` colada") atende ao desenho; os dois cortes de texto nos passos 4 e 8 mantêm o sentido.
- `LINHA_DO_ONDE` casa com as linhas reais do `bin/forge_onde.py` (todas começam por `onde: `); âncora de início de linha recusa o `onde:` no meio da frase, coberto pelo teste.
- Só mede, nunca bloqueia (ADR 0003): o campo vai só à linha de `mensagens.jsonl`, sem saída de bloqueio.

## Achados
- A1 (bloqueante) hooks/meta.py:246 · Conta a afirmação no texto inteiro; o desenho aceito (docs/propostas/v0479-melhorias-anti-erro.md:147) manda contar só fora de citação e código. Procure a afirmação em fora_de_codigo_e_citacao(texto), mantenha o onde: no texto todo e ajuste comentário e changelog.
- A2 (bloqueante) tests/test_meta.py:509 · O teste fixa o contrário do desenho (citação e bloco cercado contam). Inverta-o, com caso misto (afirmação fora e dentro) e mutante novo para a troca de fora_de_codigo_e_citacao(texto) por texto.

## Sondas
- S1 · afirmacao_sem_prova("> mesclado") · espera: False (só citação) · obtido: True
- S2 · afirmacao_sem_prova("```\nintegrado\n```") · espera: False (só bloco de código) · obtido: True

## Parecer
Reprovado. Mecânica correta e mutantes mortos, mas a regra de contagem contraria o desenho aceito pelo dono (A1) e o teste a fixa (A2). A correção é pequena e reaproveita `fora_de_codigo_e_citacao`.
