---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: f50171d232c95fa4562422bcda5f92a144a8a586
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (AE7.1, forge-check comparar, etapa E58.34)

Escopo: `bin/forge_comparar.py`, o subcomando em `bin/forge-check`, `tests/test_comparar.py` (30 testes), o corpus `tests/comparar/corpus.jsonl` (215 casos) e as quatro specs `tests/mutantes/v0478-ae7-comparar*.json`. Sem suíte local; a suíte inteira é do CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Head que libera o que a base recusava aparece como aceite-novo (rc 1) | Medida.test_head_que_libera_aparece_como_aceite_novo; Subcomando.test_forge_check_comparar; prova sintética abaixo | recusa → aceite | passou |
| Head que aperta ou árvore igual mede zero (rc 0) | Medida.test_head_que_aperta_nao_conta, test_mesma_arvore_mede_zero | árvore idêntica | passou |
| Pergunta no lugar da recusa conta como aceite-novo | Medida.test_pergunta_no_lugar_da_recusa_e_aceite_novo | degrau recusa/pergunta/aceite | passou |
| Hook que estoura o prazo, saída não JSON, matcher que deixa de casar, hooks.json ilegível: contam como liberado | Medida.test_hook_que_passa_do_prazo_libera, test_saida_que_nao_e_json_libera, test_matcher_que_deixa_de_casar_libera, test_hooks_json_ilegivel_no_head_e_nenhum_hook | prazo, JSON inválido | passou |
| Caso removido do corpus pelo head não escapa (corpus-removido) | Corpus.test_head_que_tira_o_caso_nao_escapa, test_head_sem_o_arquivo_do_corpus_tira_todos | corpus vazio | passou |
| Corpus ilegível, sem casos, blob ilegível: não verificável (rc 2) | Corpus.test_corpus_ilegivel_e_nao_verificavel, test_nenhum_caso_e_nao_verificavel, test_blob_que_nao_se_le_e_nao_verificavel | vazio, ilegível | passou |
| Ref hostil não chega ao git; link para fora da árvore não é extraído; archive falho é não verificável | Refs.test_ref_com_opcao_ou_intervalo_nao_chega_ao_git, test_link_para_fora_da_arvore_nao_e_extraido, test_archive_que_falha_e_nao_verificavel, test_rev_parse_que_falha_nao_vale, test_commit_de_outro_repositorio_e_nao_verificavel | `-x`, `..`, symlink | passou |
| Hook roda como o Claude Code (ambiente por lista positiva, variável ausente) | ComoOClaudeCode.* | ambiente mínimo | passou |

## Provas
Vermelho antes do verde (`bin/forge-testes --vermelho b14f2e19 --modulos test_comparar --prazo 1100`, rc 0):
```
vermelho: base=b14f2e1952cd head=5961e2f3a30a módulos=test_comparar (restrito por --modulos)
tests.test_comparar.Subcomando.test_forge_check_comparar · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=29; prova (asserção)=1
```
Os 29 que passam na base testam `bin/forge_comparar.py`, que a base não tem: `forge-check` da base não carrega o módulo e o teste de subcomando cai na base. Nenhum teste cai no head; o veredito é prova (rc 0). A prova do comportamento dos 29 está nos mutantes abaixo.

Mutantes (uma chamada por spec, todas rc 0, 31 mutantes, 31 morreram, 0 sobreviventes, 0 equivalentes, 0 sem veredito):
```
spec comparar.json    CMP1-CMP8   morreu x8   (CMP3, CMP4, CMP5 com (erro))
spec comparar-2.json  CMP9-CMP16  morreu x8   (CMP15 com (erro))
spec comparar-3.json  CMP17-CMP24 morreu x8   (CMP23 com (erro))
spec comparar-4.json  CMP25-CMP31 morreu x7   (CMP31 com (erro); CMP29 em bin/forge-check:10492)
```
Cobertura (`bin/forge-mutante --cobertura --base b14f2e19`, rc 0): `base=b14f2e1952cd… rev=5961e2f3a30a…`; toda condição Python mudada em `bin/forge_comparar.py` sai `coberta · … · declarado, não provado` (agora provada pelas rodadas acima); uma `isenta` (linha 138, número de trabalhadores do pool, só muda o tempo: justificativa aceita); `não coberto` só em dados (`dev/.claude-plugin/plugin.json`, `tests/comparar/corpus.jsonl`, `tests/pesos-d4.json`), sem lógica de guarda.

Teste de afrouxamento real (clone descartável em `/root/.forge-contrib/wt/qa181-clone`, o head 5961e2f3 com `hooks/hooks.json` trocando `hooks/parecer.py` por `/dev/null`, ou seja, o hook de parecer deixa de recusar):
```
forge-check comparar 5961e2f3 <commit-sintético>   → rc=1
so-aperta: medido base=5961e2f3… head=fa6e9d8e… casos=215 aceites-novos=3
aceite-novo: parecer/heredoc-interpretador-python-asyncio-exec-git-pull-bloqueia base=recusa head=aceite
aceite-novo: parecer/heredoc-interpretador-python-lista-em-duas-linhas-bloqueia base=recusa head=aceite
aceite-novo: parecer/heredoc-interpretador-python-os-system-pull-bloqueia base=recusa head=aceite
```
Controle (base antiga b14f2e19 contra o head, só apertos e adições): `forge-check comparar b14f2e19 5961e2f3` → rc=0, `casos=215 aceites-novos=0`. Observação: base antiga real só com hook afrouxado e corpus já existente não existe no histórico (o corpus nasce neste pedido); por isso o afrouxamento foi sintético sobre o head, com a base sendo o head limpo.

`python3 -I -m unittest discover -s tests -p test_comparar.py`: 30 testes, OK. Árvore do autor limpa após as rodadas.

## Cenários e resultado real
Aprovado. Sem bug aberto. Saídas completas em `/root/.forge-contrib/wt/qa181-*.txt`.

## Revalidação no head 3d0bdaf9 (E58.38, escopo incremental)
Delta lido por `forge-check parecer delta` (intervalo 5961e2f3..3d0bdaf9): `bin/forge-check` (só a ajuda do subcomando), `bin/forge_comparar.py` (blob a blob no lugar de `git archive`, lados separados, veredito de 4 níveis com `updatedInput`), `tests/test_comparar.py`, specs `tests/mutantes/v0478-ae7-comparar-2..7.json` (agora 7 specs), `changelog.d`. Saídas em `/root/.forge-contrib/wt/qa-e5838-out/`.

- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 42 testes, OK (rc 0).
- Mutantes, uma chamada por spec, todas rc 0, `rev=3d0bdaf9089f`: spec base 8, -2 8, -3 8, -4 7, -5 8, -6 8, -7 2 = 49 mutantes, 49 morreram, 0 sobreviventes, 0 sem veredito.
- `bin/forge-mutante --cobertura --base 821db42e` (rc 0): `base=821db42ed97e… rev=3d0bdaf9089f…`; 35 condições `coberta`; uma `isenta` (`bin/forge_comparar.py:160`, teto do pool, só muda o tempo); `não coberto` só em dados (`tests/comparar/corpus.jsonl`, `tests/pesos-d4.json`). Nenhuma `isenta velha`.
- Afrouxamento sintético 1 (clone `/root/.forge-contrib/wt/qa-e5838-clone`, `hooks/hooks.json` com `hooks/parecer.py` trocado por `/dev/null`): `forge-check comparar 3d0bdaf9 c1bd526b` rc 1, `casos=215 aceites-novos=3` (heredoc-interpretador python x3, `base=recusa head=aceite`).
- Afrouxamento sintético 2 (mesmo clone, `hooks/parecer.py` responde `permissionDecision: allow` em tudo): rc 1, `casos=215 aceites-novos=215`, com `base=recusa head=allow` e também `base=aceite head=allow` (o 4º nível pega o allow explícito).
- Controle: `forge-check comparar 5961e2f3 3d0bdaf9` rc 0, `casos=215 aceites-novos=0`, com a linha `so-aperta: medido base=… head=…`.
- Árvore do autor limpa após as rodadas.

Resultado: aprovado no head 3d0bdaf9; sem bug aberto.

## Revalidação no head f50171d2 (E58.47, escopo incremental)
Delta lido por `forge-check parecer delta` (intervalo 3d0bdaf9..f50171d2): `bin/forge_comparar.py` (A1 decisão `approve`, A2 `.gitattributes`, A7 matcher fora da forma simples, A8 saída não UTF-8, TMPDIR próprio, A9 caso recusado sem reescrita, A10 hooks fora do `hooks/hooks.json`), `tests/test_comparar.py`, specs `-4`, `-6`, `-8`, `-9`, `-10`, `changelog.d`. O comentário com nome de stack, que reprovou o head bddae43f, saiu em 339cf138. Saídas em `/root/.forge-contrib/wt/qa-e5847-out/`; TMPDIR próprio; `timeout 1500` em primeiro plano.

- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 53 testes, OK (rc 0).
- Mutantes, uma chamada por spec, todas rc 0, `rev=f50171d232c9`: -4 7 (CMP25-CMP31), -6 8 (CMP40-CMP47), -10 7 (CMP61-CMP67) = 22 mutantes, 22 morreram, 0 sobreviventes, 0 sem veredito (CMP26 e CMP31 com `(erro)`, teste declarado dá erro sob o mutante e passa sem ele). Um mutante por linha de guarda mudada no delta: A10 (linhas 72-90), reescrita (232-233), TMPDIR e UTF-8 (186-199), decisão antiga (161).
- `bin/forge-mutante --cobertura --base 821db42e` (rc 0): `base=821db42ed97e… rev=f50171d232c9…`; 47 condições `coberta`; uma `isenta` (`bin/forge_comparar.py:203`, teto do pool, só muda o tempo); `não coberto` só em dados (`tests/comparar/corpus.jsonl`, `tests/pesos-d4.json`). Nenhuma `isenta velha`.
- Sonda de hook declarado, clone descartável `/root/.forge-contrib/wt/qa-e5847-clone` sobre f50171d2:
  - chave `hooks` somada ao `.claude-plugin/plugin.json`: `forge-check comparar f50171d2 <sonda>` rc 2, `so-aperta: nao-verificavel (hooks declarados em .claude-plugin/plugin.json)`.
  - `hooks:` no cabeçalho YAML de um agente `.md`: rc 2, `so-aperta: nao-verificavel (hooks declarados no cabeçalho de agente ou skill)`.
  - controle, `forge-check comparar f50171d2 f50171d2`: rc 0, `casos=215 aceites-novos=0`, com a linha `so-aperta: medido base=… head=…`.
- Árvore do autor limpa após as rodadas.

Resultado: aprovado no head f50171d2; sem bug aberto. O reprovado anterior (bddae43f, comentário com nome de stack) está sanado.

## Achados
Nenhum.
