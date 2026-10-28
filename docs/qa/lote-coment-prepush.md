---
tipo: qa
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: 1c1d68de42a42eae7f354cb173b1496f441e165e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: lote-coment-prepush

Pedido LOTE-COMENT-PREPUSH-REV (E3.1), volta 2 pela decisão B do dono de 2026-10-27 08:33. Só texto e teste: o README (Suíte do Forge) vira uma regra fechada pelo complemento e a asserção estrutural substitui o teste de termos soltos. Base 739b0b083d2baacefdf4f7482b2b2ac31ed8e02c, head 1c1d68d (o parecer anterior era sobre 70ba6c6). `.githooks/pre-push` e `bin/forge-testes` não mudam nesta volta (diff 70ba6c6..1c1d68d: README, `tests/test_forge.py`, `tests/test_testes_tocados.py`, fragmento de changelog).

## Achados
Nenhum. O A1 recomendado da volta 1 (`.githooks/pre-push:236` cita 2026-10-23) segue fora do escopo do lote, para lote próprio, e não devolve.

## Critério → teste → resultado
Sem especificação de UX nem `CA-n`; as obrigações são as do escopo E1 do pedido e a decisão B.

| Obrigação | Teste | Resultado | Fronteira protegida |
|---|---|---|---|
| E1: README cita os casos de suíte inteira (`sem tocar bin/forge-testes, tests/config.json ou .githooks/`) e o caminho só de parecer | `tests.test_forge.PrePushSoOsAfetados.test_readme_cita_os_casos_da_suite_inteira_e_o_caminho_so_de_parecer` | passa no head; falha em 70ba6c6 | n/a |
| Decisão B (4.1/4.2): toda frase com "só os testes afetados" traz as condições do envio simples (uma só ref, árvore limpa, HEAD igual, `origin/develop`); "Qualquer outro envio roda a suíte inteira"; sem "árvore suja", "mais de uma ref", "HEAD diferente", "segue a regra acima"; cita `so_parecer` e `dirigido` | `...PrePushSoOsAfetados.test_readme_so_diz_afetados_para_o_envio_simples_e_o_resto_e_suite_inteira` | passa no head; falha em 70ba6c6 | limite do envio simples (as condições nomeadas na mesma frase) |
| E1: docstring cita M8; docstring não manda review e QA rodarem a suíte inteira | `tests.test_testes_tocados.NaoEPortao` (dois testes da volta 1, sem mudança de código) | passam no head | n/a |
| Só texto, nenhum comportamento muda | `.githooks/` e `bin/` intactos nesta volta + `test_forge` e `test_testes_tocados` inteiros | 512 testes OK | n/a |

## Conferência do README contra o hook, caso a caso (`.githooks/pre-push` no head)
A regra nova: afetados só num envio simples de `melhoria/*` (uma ref, árvore limpa, HEAD igual, `origin/develop`, todo caminho com regra, sem tocar `bin/forge-testes`, `tests/config.json`, `.githooks/`); o resto é suíte inteira; exceção curta de pareceres; a fonte é o hook.
- Mais de uma ref: `dirigido` recusa (`n_refs` diferente de 1, linha 251) e `so_parecer` recusa (214) → suíte inteira. README confere (cai em "qualquer outro envio").
- Árvore suja: `dirigido` 257 e `so_parecer` 218 recusam → suíte inteira. Confere.
- HEAD diferente do commit enviado: `dirigido` 256 e `so_parecer` 217 recusam → suíte inteira. Confere.
- Ref fora de `melhoria/*`: `dirigido` 252 recusa → suíte inteira (ou, se só parecer sobre prova, as classes curtas, que o README traz como exceção). Confere.
- Diff em `bin/forge-testes`, `tests/config.json` ou `.githooks/`: 265 recusa → suíte inteira. Confere.
- Só pareceres: `so_parecer` roda as classes que leem pareceres com os pré-requisitos do README (branch existente = remoto não zero 221-222, árvore limpa, HEAD igual, árvore remota com prova `.verde` 219-224, sem remoção ou renomeação 225, sem `_*`, `ameacas/`, `aceites/` 229-231, só os quatro diretórios 232). Confere. Fora dessas condições cai no `dirigido` ("segue a regra de cima"), conforme a ordem `so_parecer` → `dirigido` → suíte inteira (270-277). Confere.
- Sem `origin/develop`, plano que não começa por `forge-testes: dirigido (` e caminho sem regra: 259 e 266-268 → suíte inteira. Confere ("origin/develop presente", "todo caminho com regra").
- Sem ref ou só remoção, e push misto: parágrafo e hook inalterados (140-155). Confere.
O README não descreve caso que o hook não faça nem omite caso que o hook trata de outro jeito. Observação sem custo: a exceção diz "uma branch" sem escrever "uma só ref"; a ressalva já está na regra de cima e na frase "fora dessas condições o envio segue a regra de cima".

## Vermelho antes do verde
`bin/forge-testes --vermelho 70ba6c6` (rc 0, o conjunto completo de módulos); linhas que provam:
```
vermelho: base=70ba6c614bda head=1c1d68de42a4 módulos=test_changelog,test_citacao,test_clareza,test_dependabot_modelo,test_doutor,test_erros_no_brief,test_forge,test_forge_mutante,test_modelos_citados,test_modelos_projeto,test_novo_projeto,test_sobreposicao_quadro,test_stack_prereq_sistema,test_textos_dono_f10,test_textos_dono_f7
tests.test_forge.PrePushSoOsAfetados.test_readme_cita_os_casos_da_suite_inteira_e_o_caminho_so_de_parecer · H=ok · B=falha · prova (asserção)
tests.test_forge.PrePushSoOsAfetados.test_readme_so_diz_afetados_para_o_envio_simples_e_o_resto_e_suite_inteira · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=739; prova (asserção)=2; pulado=1
```
Nenhum teste cai no HEAD.

## Execução
`python3 -m unittest tests.test_forge tests.test_testes_tocados` no head: Ran 512 tests, OK. Suíte completa e CI não rodados aqui (pre-push e CI do PR cobrem). Mutação: não se aplica (nenhuma linha de guarda em `bin/`, `hooks/`, `.githooks/` mudou nesta volta).

## Parecer
Aprovado. Zero bugs; zero achados.
