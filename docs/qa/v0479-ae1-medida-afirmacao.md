---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-medida-afirmacao
commit: f15b9b85e5c42f9310f7523fc2c25c5a35b8d3b4
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-ae1-medida-afirmacao (AE1.4, E58.20)

Diff conferido contra a base ed5bfa02: `hooks/meta.py` (campo `afirmacao_sem_prova` em `mensagens.jsonl`), `agents/jarvis.md` (colar a linha `onde:`), `tests/test_meta.py`, spec de mutantes e changelog. Obrigação: desenho AE1.4 em `docs/propostas/v0479-melhorias-anti-erro.md:147` (só mede, nunca bloqueia; lista de palavras fixa; conta o texto fora de citação e código), ADR 0003, R-QA.

## Achados
- A1 (bloqueante) hooks/meta.py:240 · conta feito/mesclado/integrado dentro de citação e código; o desenho (propostas:147, ERRO-JARVIS 18:02 do pedido) manda contar fora dos dois. `afirmacao_sem_prova("> mesclado")` dá True. Bug em docs/qa/bugs/.
- A2 (bloqueante) tests/test_meta.py:502 · os 4 testes novos caem na base por KeyError, não por asserção; `forge-testes --vermelho` sai 2 (sem veredito), que não vale como vermelho (R-QA). Ler com `.get("afirmacao_sem_prova")` para falhar por asserção.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Afirma sem `onde:` marca (feito, mesclado, integrado; flexão, caixa) | test_afirmacao_sem_a_linha_do_onde_conta | palavra inteira (perfeito não conta) | passou |
| Linha `onde: <algo>` no início da linha prova (texto, citação, código) | test_a_linha_do_onde_colada_e_a_prova_em_texto_citacao_ou_codigo | prefixo `> `, crases e espaços | passou |
| `onde:` fora do início ou vazio não prova; sem afirmação não marca | test_sem_afirmacao_ou_com_onde_fora_do_inicio_da_linha_nao_prova | `onde:` sem conteúdo, no meio da linha | passou |
| Conta no texto fora de citação e código (desenho) | test_afirmacao_escondida_em_citacao_ou_codigo_tambem_conta (afirma o contrário) | citação e bloco de código | reprovou o desenho (A1) |
| Só mede, nunca bloqueia (ADR 0003) | 36 testes de `test_meta` | n/a | passou: a medida só grava o campo |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_meta.py` com TMPDIR: 36 testes, OK.
- Vermelho: `forge-testes --vermelho ed5bfa02 --modulos test_meta`, rc=2:
  `vermelho: base=ed5bfa0284c3 head=f15b9b85e5c4 módulos=test_meta (restrito por --modulos)`;
  `revertidos à base: agents/jarvis.md, changelog.d/v0479-ae1-medida-afirmacao.md, hooks/meta.py`;
  as 4 `AfirmacaoSemProva.*` saem `H=ok · B=erro · sem veredito`; `contagem: não prova (passa na base)=32; sem veredito=4`. Reproduzido à mão na base: `KeyError: 'afirmacao_sem_prova'` (12 erros, 4 testes).
- Mutação: `bin/forge-mutante tests/mutantes/v0479-ae1-medida-afirmacao.json`, rc=0: M1 a M6 `morreu` (meta.py:246, 246, 241, 241, 240, 240). `--cobertura --base ed5bfa02`: `coberta · hooks/meta.py:246 · M1, M2 · declarado, não provado`; as linhas 240 e 241 são constantes de regex, mutadas por M3 a M6. Sem sobrevivente.
- Bordas lidas no código: "perfeito" não casa (limite à esquerda); "feitas", "INTEGRADAS" casam; texto cortado em TETO_DA_MEDIDA mede só o início (já documentado).
- Suíte inteira não rodada aqui; vale o check-run `bateria` do CI do mesmo sha.

## Prova do A1 após a correção
A volta troca o teste de citação/código para afirmar o desenho (fora dos dois: conta; dentro: não) e atualiza o mutante M-novo para a chamada de `fora_de_codigo_e_citacao`.
