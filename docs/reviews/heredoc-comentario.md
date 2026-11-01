---
tipo: review
contrato: 1
pedido: heredoc-comentario
branch: melhoria/heredoc-comentario
commit: 262535c43f124882155c67d9fbd89b2bba788c2b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-01
---
# Review: heredoc-comentario (E1.2)

## Revalidação no 262535c (volta por delta)
`forge-check delta --parecer docs/reviews/heredoc-comentario.md`: intervalo `1fa4398..262535c` (o merge da develop f534013, heredoc-rapido passo 2). Lido o que ele lista: `hooks/_comum.py` 822-855, 990, 1281, 1757-1781; `tests/test_hooks.py` 1682-1706, 1828-1846, 1875; as 6 fixtures `heredoc-marca-c8*`, `tests/mutantes/heredoc-rapido-p2.json` e `changelog.d/heredoc-rapido-p2.md` (estes do PR #422, já revisados lá; conferi só que não alteram esta branch). Lidos também `git show --cc 262535c` (os dois conflitos resolvidos) e `git diff f534013 262535c`.
- `hooks/_comum.py`: `montar` ficou o desta branch; `citadas` troca o `re.sub` com `MARCA` por `MARCAS.sub` (`_comum.py:848`, fonte única do passo 2, com `MARCA = "__fh"`). Aplicar por linha equivale ao texto juntado da develop: a marca não atravessa a quebra de linha. `segmento` lê `partes` e `indice.mesmo`, que o passo 2 não muda.
- Oráculo C-1 (`test_hooks.py:1862`): o `montar` dele é agora o da develop f534013 (com `MARCAS`), linha a linha; segue valendo como base.
- Teste do orçamento (`test_hooks.py:1820`): as 4 formas da develop e as 6 desta branch, cada uma com a recusa esperada: teto de palavras em `x=$(` (develop) e em ` x#c`, `cat a<i> # c`, `| cat > f # c` (como no 1fa4398); as demais, a R-MAIN da fixture. Nenhuma expectativa caiu.
- Rodado no 262535c: os 4 testes da branch, `Ran 4 tests in 153.824s OK`; as 10 fixtures `heredoc-comentario-*` e `heredoc-marca-*` pelo `executar_em_lote`, OK. Vigia de produção: C-6 (b) R-MAIN em 2,11 s (antes 2,3 a 2,5), (a) R-MAIN em 1,53 s, (c) teto de palavras em 0,99 s, (d) `.claude/**` em 1,76 s.
- M14 no head: `git diff --numstat --no-renames origin/develop...HEAD` (develop 91d6cc1): `hooks/_comum.py` 40+12, `tests/test_hooks.py` 89+7: **148 de 150**, uma classe de comportamento em `hooks/`. `git merge-tree` com a develop atual: limpo.
- Já lido no parecer do 1fa4398 e fora do delta: o resto de `montar`, `segmento`, `vestir`, os testes C-1, C-4, C-5 e as 4 fixtures C-6.

## Parecer do 1fa4398 (base da revalidação)

Diff lido: `e25d379..1fa4398` (4 commits). Referências: proposta `docs/propostas/heredoc-comentario.md` (E1.0) e modelo `docs/security/ameacas/heredoc-comentario.md` (C-1 a C-7, T1 a T6). Revisor não é o autor (D-ETAPAS-INST).

## M14 (teto e comportamento)
`git diff --numstat --no-renames e25d379 1fa4398`: `hooks/_comum.py` 40+12 = 52; `tests/test_hooks.py` 85+3 = 88. Total que conta: **140 de 150**. Fora da conta: `changelog.d/`, as 4 fixtures de `tests/hooks/` e `tests/mutantes/heredoc-comentario.json`. Sem linha de exceção e sem precisar dela (`hooks/` é PROTEGIDO). Uma classe de comportamento em `hooks/` (custo da montagem dos donos), com corpus próprio (4 fixtures C-6). Cumpre a M14.

## Ferramentas
O Forge não tem `docs/engineering/praticas.md` com regras "ferramenta"; cito o que o autor e eu rodamos. Pre-push do autor verde (registro no pedido, 12:31). Rodados aqui no head revisado: `test_donos_dos_heredocs_iguais_aos_da_base`, `test_dono_largo_acima_do_teto_de_custo`, `test_forma_com_comentario_recusa_pela_regra_com_o_vigia_de_producao` e `test_muitos_heredocs_recusam_dentro_do_orcamento`: `Ran 4 tests in 161.511s OK`. Mutação: spec com M1 a M12 (13 mortos, segundo o autor); não refeita.

## Leitura do código contra o desenho e os controles
- `segmento` cacheia por `(k, sub, ini, fim)`: mais estreito que o `(nível, ini, fim)` que o T3 aceita. Chave do texto por `id` dos segmentos internados em `self.iguais`/`self.citados` (vivos durante o objeto, então o `id` é estável); o texto do ramo com `trechos` só depende desses segmentos. `lugar` segue na chave de `vistos`. Sem T3.
- A leitura legado continua nas `partes` e em todos os donos (sem T1); nada truncado nem deduplicado fora de igualdade exata de conteúdo (sem T2, T4); `trechos is None` segue pelo `resto` lógico (sem T5).
- C-4: o gasto soma só texto novo; passou de 150 mil, o dono de todo heredoc seguinte vira o largo (todas as leituras inteiras mais o `resto`, vestido com `fora_do_texto`); com o `resto` acima do teto, `ValueError`, que o chamador já recusa. Só alarga ou recusa (sem T6). Diferença em relação ao C-4 do modelo (conta na montagem, não antes de `leituras`) está declarada na proposta (f) e é para o E1.3 julgar.
- C-1: oráculo dentro da suíte com o `montar` da develop por `mock.patch`; mais de 4.200 linhas (fixtures com `<<` e a matriz de 4.116, asserção do teste). Contei a matriz: 336 linhas ilegíveis nas duas leituras (separador com continuação), o resto todo comparado dono a dono.
- C-2: medido aqui pelo hook real com o vigia de produção, `# c`: 1000 0,65 s; 2000 1,27 s; 3000 1,86 s (linear, razão 2,9). C-3: as cinco formas e `cat a<i> # c` no teste do orçamento, com a recusa da develop (teto de palavras nas três de 6004 palavras). C-7: comentário de `_comum.py:2421` corrigido.
- Fixtures C-6 pelo hook (vigia de teste e de produção): (a) R-MAIN em 1,8 s; (b) R-MAIN em 2,3 a 2,5 s.

## Riscos citados pelo autor
- C-6 (b) com `"stderr": "R-"`: a recusa sai pela R-MAIN aqui, mas a 2,5 s do `PRAZO_DA_LINHA_S` (3 s, `conformidade.py:40`); no CI (2,6 a 3,1 vezes mais lento) virá pelo prazo da linha, que também fecha. O C-6 (b) pede recusa, não a regra; a lógica do `| bash` no último dono fica provada sem relógio no `test_dono_largo_acima_do_teto_de_custo` e no `cat | bash` da matriz do oráculo. Aceito, com A1.
- C-6 (e) sem fixture própria: a suíte roda o vigia em 120 s, então a fixture (a) e o teste do orçamento já medem a decisão sem vigia efetivo, abaixo de 5 s. O que falta é a plataforma sem `SIGALRM` de verdade; é do QA (E1.4). A2.
- Folga do C-5: 0,65 s aqui contra 3 s do vigia; no CI, ~2 s. Folga de ~1,5 vez. A3.

## Achados
- A1 (recomendado) tests/hooks/conformidade/heredoc-comentario-3000-bash-no-ultimo-push-main-no-corpo-bloqueia.json:28 · "R-" aceita qualquer recusa; no CI pode sair pelo prazo (R-MAIN aqui em 2,1 s de 3 s). Fecha; o `| bash` está provado sem relógio no teste C-4; o QA registra a recusa do CI.
- A2 (recomendado) tests/test_hooks.py:1820 · C-6 (e) sem fixture própria: o vigia de 120 s da suíte cobre a decisão sem prazo efetivo; falta só a plataforma sem SIGALRM, a registrar no QA (E1.4).
- A3 (recomendado) tests/test_hooks.py:1923 · folga do C-5 de ~1,5 vez no CI (0,65 s aqui contra o vigia de 3 s); o QA mede o tempo desse teste no run do PR.
- A4 (recomendado) tests/test_hooks.py:1900 · `dono[0] == "e"` lê-se invertido (o `)"` vai para os donos sem `eval`); medi que as 1.372 linhas dessa variante são legíveis e comparadas, então não perde cobertura; um comentário com a intenção basta.
- A5 (recomendado) tests/test_hooks.py:1864 · a docstring do oráculo diz `montar` da develop e25d379; depois do merge ele é o da f534013 (com `MARCAS`). Trocar a referência, sem mudar a lógica.

## Parecer
Aprovado no 262535c: o merge da develop preserva o desenho, as recusas e os controles; A5 é nova e recomendada. Cumpre a M14 (148 de 150 no head, 140 no 1fa4398, uma classe de comportamento em `hooks/`), segue a proposta E1.0 e não toca nenhum dos T1 a T6; C-1, C-2, C-3, C-4 e C-7 conferidos na leitura e na execução; C-5 e C-6 com folga e cobertura que o QA confirma no CI (A1 a A3). Nenhum achado bloqueia. Segurança (E1.3) e QA (E1.4) dão os seus pareceres; não os refaço.
