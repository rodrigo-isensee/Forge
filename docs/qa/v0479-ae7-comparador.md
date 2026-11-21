---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 5961e2f3a30a4209a940a9745fe02a1b3a24f39c
parecer: aprovado
escopo: completo
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
