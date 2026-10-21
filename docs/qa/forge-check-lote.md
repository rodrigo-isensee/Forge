---
tipo: qa
contrato: 1
pedido: forge-check-lote
branch: melhoria/forge-check-lote
commit: 9c09ae01ce0dba86cf150d1853a695f111837ffd
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: forge-check-lote (E1.4)

Pedido sem UX nem API: o lote muda `bin/forge-check`, `agents/conferente.md`, testes e docs. Código testado: `9c09ae0` (HEAD remoto `4da21d0` só traz os pareceres de review e segurança por cima). Não escrevi o diff. Review e segurança aprovados sobre `9c09ae0`. Sem teste novo de minha autoria: a obrigação de cada item já tem teste do autor, cujo vermelho antes do verde e cuja mutação estão no parecer do review (E1 4/4, E4 5/6, E6 4/4, E9a 8/9; vivos explicados em R4 e R5); aqui exercitei o comando de ponta a ponta.

## Achados
- A1 (recomendado) bin/forge-check:764 · `entrega --brief` reprova com `escopo: união de briefs de entregas diferentes` quando o brief traz `Pedido:` como caminho (os briefs deste lote o trazem); só o id passa. Normalizar o caminho ou o conferente passar o id.

## Execução
- `.githooks/pre-push --status` antes: rc=0 (outra suíte rodando); esperei a trava (R-TETO) e rodei sob a mesma trava.
- `python3 -m unittest discover -s tests -q` na raiz da worktree: `Ran 1171 tests in 262.635s` / `OK`. Nenhum teste falhou e passou de novo sem mudança (FLAKY-CARGA: nenhum nome a registrar). `actionlint` ausente no PATH só pula o lint de workflow (aviso do próprio teste).
- `scripts/validar-plugin.sh`: `Validation passed` (aviso de ícone ausente não muda o resultado; rede negada no sandbox, esperado).
- Sondas numa cópia em `$TMPDIR` (clone da branch, remoto bare local, nada tocou `origin` real nem a worktree).

## Obrigação -> teste -> resultado
| Item | Comando exercitado (cópia em `$TMPDIR`) | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (O1) | `forge-check pr`/`brief` com a cópia vigente atrás: `forge-check: aviso: cópia vigente 0.26.0 (commit 4da21d0) atrás do repositório (decisão D: não muda o veredito)...`; resultado `aprovado`, rc 0 | só estado `atrasada` no Forge; `agents/conferente.md` repete a frase | funciona |
| E2 (O3=B) | `brief gerar --volta docs/briefs/...-1.md --ref volta-sim --incluir docs/reviews/forge-check-lote.md:R1`: Entregar traz `(review 448b479 A1) ...` e `(incluído review 448b479 R1 de docs/reviews/forge-check-lote.md) <texto literal> [bin/forge-check:700]`; Objetivo, Fora do escopo, Decisões e Pronto copiados idênticos | recomendação lida só da `--ref` | funciona |
| E3 (O5) | `agents/conferente.md:78`: "Não rode a suíte (`python3 -m unittest`) nem `scripts/validar-plugin.sh`, nem para conferir" | texto | funciona |
| E4 | com o merge da develop (README alheio) `pr --ref sim-merge --base develop` rc 0; sem `--base` o mesmo caso: `desatualizado: README.md mudou...`; mudança em `bin/forge-check` na branch depois do parecer com `--base develop` ou `--base origin/develop`: `desatualizado: bin/forge-check mudou depois do parecer ... (base origin/develop 5393167)`, rc 1; `--base sim-merge` (o próprio head): `pr: --base "sim-merge": use develop, homolog, main (ou origin/<uma delas>)`, rc 1; develop local atrasada não encolhe o diff (lê `origin/`) | arquivo do pedido mudou; base falsa; base local atrasada | funciona |
| E5 | `entrega ... --etapa seguranca` aceito (intervalo e `escopo:`); com `--desde` válido idem; `--etapa pr --desde` reprova `escopo: --desde fora da etapa`; aviso de versão tratado como E1 | etapa nova no vocabulário | funciona |
| E6 | linha do pedido com a frase no meio: `decisões: menção fora do início docs/pedidos/forge-check-lote.md:85 (informativo; não cobrada)`, `aprovado`; linha que abre com a frase e ausente do brief: `decisões: falta ...`, `reprovado` | âncora no início da linha | funciona |
| E7 | `entrega` com arquivo de nome com `\n`, U+2028 e ESC: `escopo: confira "ev\nil: resultado aprovado z.txt" +1 -0` e `"x\u001b[31m.txt"`; raiz com `\n` e U+2028 no nome não vaza em `pr` | quebra de linha, Zl e C1 em caminho impresso | funciona |
| E8 | `transcricao custo --desde 2026-10-20T23:00:00Z --ate 2026-10-21T01:30:00Z` acha a pasta pela raiz e imprime `custo: janela: fora_da_janela=220919`; `--desde lixo`: `hora "lixo" fora de ISO 8601`; `--desde` depois de `--ate`: recusa; `--raiz ~/.forge-contrib --pedido conf-anexo-pareceres <pasta>`: `custo: pedido: ... janela 2026-10-17T17:29:30-03:00 a 2026-10-17T18:53:10-03:00` e `aviso: 2 outros cartões em movimento na janela`; cartão com um só movimento: `nenhuma mensagem com usage` (janela vazia, mensagem clara); sem rede (só disco) | janela vazia, hora inválida, invertida | funciona |
| E9a | `entrega --brief` (2 briefs, mesma Branch, Base, Base-sha, pedido): `brief: ... sha256 ...` por brief e `escopo: união de 2 briefs (mesma Branch, Base, Base-sha e pedido)`; com `--desde f1dbe10`: `intervalo: f1dbe10..4da21d0` e só 4 arquivos; brief de outra branch reprova | união só do mesmo conjunto | funciona, ver A1 |
| E9b | `conferente.md:16` (dois blocos, `modo: brief` até `BRIEF>>>` e `modo: entrega` depois; um bloco de saída por bloco); `brief mensagem` imprime `BRIEF>>>` no fim; o julgamento do conferente (agente) não é exercitável sem subagente | só texto | texto confere; julgamento fora do alcance da sonda |
| E9c | `brief mensagem --pedido ... --arquivo docs/briefs/...-qa-engineer-1.md --etapa E1.4` sem `--destino`: `Agente destino: forge:qa-engineer`; `--destino forge:tech-lead`: `--destino difere do Agente destino: do brief`, rc 2; `--destino` igual passa; `Arquivo:` sai `/tmp/claude-1000/cp/docs/briefs/...` (absoluto); `--arquivo` fora de `docs/briefs/` recusado; `--help` explica quando `--destino` é preciso | destino divergente, arquivo fora da pasta | funciona |
| E9d | `--etapa $'E1\x07'`: `o campo --etapa tem o caractere de controle ou de formato U+0007`, rc 2; U+2028 idem; o valor não é ecoado | campo nomeado e U+XXXX | funciona |
| E10 | suíte 1171 OK; `changelog.d/forge-check-lote.md` presente com entrada `### Alterado`; invariantes só por acréscimo (suíte verde) | n/a | funciona |
| E11 | `brief gerar --branch melhoria/nova-x` (branch inexistente): `Base-sha: 539316749dc3...` igual a `origin/develop`; branch existente: o merge-base `0f480c8` (igual ao `git merge-base`); `brief` com Base-sha `deadbee...` fora da branch: `aviso: Base-sha deadbee do brief não está na branch melhoria/forge-check-lote; gere o brief de novo (BRIEF-BASE-ATUAL)`, resultado `aprovado` (só avisa) | branch inexistente; Base-sha fora da branch | funciona |

Casos de abuso do modelo de ameaças: os 23 têm teste do autor (suíte verde); sonda manual confirmou os de saída (E7), base falsa (E4), campo com controle (E9d) e menção fora do início (E6).

## Limites desta sonda
- Projeto sem ser o Forge (aviso de versão sem o marcador `decisão D`): coberto só pelo teste `tests/apoio_versao_defasada.py` e pela suíte; não reproduzi uma cópia vigente atrasada num projeto de fora.
- A frase "o conferente responde aos dois blocos" é comportamento de agente; só conferi o texto e o formato da mensagem.
