---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: bb1bac50822cd077f979063a93430c28a1292977
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

## Revalidação no head 757355b4 (E58.51, escopo incremental)
Delta lido por `forge-check parecer delta` (intervalo f50171d2..757355b4): `bin/forge_comparar.py` (A11 link simbólico em qualquer pasta, A12 `source` do marketplace, A13 cabeçalho YAML de `.md`), a ajuda do subcomando em `bin/forge-check`, `tests/test_comparar.py`, specs `-5`, `-7`, `-8`, `-10` e as novas `-11` e `-12`, `changelog.d`. Saídas em `/root/.forge-contrib/wt/qa-E5851-out/`; TMPDIR próprio; `timeout 1500` em primeiro plano.

- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 59 testes, OK (rc 0).
- Mutantes, uma chamada por spec, todas rc 0, `rev=757355b43bd7`: -5 7, -7 2, -8 8, -10 7, -11 7, -12 8 = 39 mutantes, 39 morreram, 0 sobreviventes, 0 sem veredito (CMP49 e CMP54 com `(erro)`: teste declarado dá erro sob o mutante e passa sem ele). A -11 cobre as linhas de A13 (96-98, 120, 134-146) e a -12 as de A11/A12 (111-152).
- `bin/forge-mutante --cobertura --base 821db42e` (rc 0): `base=821db42ed97e… rev=757355b43bd7…`; 56 condições `coberta`; uma `isenta` (`bin/forge_comparar.py:260`, teto do pool, só muda o tempo); `não coberto` só em dados (`tests/comparar/corpus.jsonl`, `tests/pesos-d4.json`). Nenhuma `isenta velha`.
- Sondas em clone descartável `/root/.forge-contrib/wt/qa-E5851-clone` sobre 757355b4:
  - controle `comparar 757355b4 757355b4`: rc 0, `casos=215 aceites-novos=0`, com a linha `so-aperta: medido base=… head=…`.
  - link simbólico para `/etc/passwd` na raiz: rc 2, `nao-verificavel (link simbólico na árvore)`; link relativo em `agents/sub/`: rc 2, igual.
  - `source` do marketplace em `./dev`, `../outro` e `/tmp/x`: rc 2, `nao-verificavel (plugin fora da raiz: source no marketplace.json)`; segundo plugin no marketplace: rc 2, igual.
- Árvore do autor limpa após as rodadas.

Resultado: aprovado no head 757355b4; sem bug aberto.

## Revalidação no head 2d1fa4fa (E58.56, escopo incremental)
Delta lido por `forge-check parecer delta` (intervalo 757355b4..2d1fa4fa): `bin/forge_comparar.py` (lista positiva de forma F1 a F7 no lugar das recusas A11 a A13), a ajuda em `bin/forge-check`, `tests/test_comparar.py`, specs ajustadas `-5`, `-7`, `-8`, `-10`, `-11`, `-12` e novas `-13` a `-16`, `changelog.d`, proposta. Saídas em `/root/.forge-contrib/wt/qa-e5856-out/`; TMPDIR próprio; `timeout 1500` em primeiro plano.

- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 63 testes, OK (rc 0).
- Mutantes, uma chamada por spec, todas rc 0, `rev=2d1fa4faf827`: -13 8, -14 8, -15 5, -16 3, -5 6, -7 2, -8 8, -10 7, -11 6, -12 8 = 61 mutantes, 61 morreram, 0 sobreviventes, 0 sem veredito (CMP49, CMP54 e CMP106 com `(erro)`: teste declarado dá erro sob o mutante e passa sem ele).
- `bin/forge-mutante --cobertura --base 821db42e` (rc 0): `rev=2d1fa4faf827…`; todas as condições `coberta`; uma `isenta` (`bin/forge_comparar.py:291`, teto do pool, só muda o tempo); `não coberto` só em dados (`tests/comparar/corpus.jsonl`, `tests/pesos-d4.json`). Nenhuma `isenta velha`, nenhuma sem mutante.
- Sondas em clone descartável `/root/.forge-contrib/wt/qa-e5856-out/sonda`, base 2d1fa4fa contra um commit que viola só o item:
  - controle `comparar HEAD HEAD`: rc 0, `so-aperta: medido base=2d1fa4fa… head=2d1fa4fa… casos=215 aceites-novos=0`.
  - F1 link simbólico: rc 2, `nao-verificavel (F1 modo 120000 na árvore)`.
  - F2 `.gitattributes`: rc 2, `(F2 .gitattributes ou .gitmodules na árvore)`.
  - F3 `settings.json` na raiz: rc 2, `(F3 settings.json na raiz)`.
  - F4 chave `hooks` no `plugin.json`: rc 2, `(F4 .claude-plugin/plugin.json fora da lista)`.
  - F5 `metadata.pluginRoot` no marketplace: rc 2, `(F5 .claude-plugin/marketplace.json fora da lista)`.
  - F6 `.md` com `hooks:` no cabeçalho: rc 2, `(F6 cabeçalho de .md fora da forma simples)`.
  - F7 matcher `Bash(.*)`: rc 2, `(F7 matcher fora da forma simples em hooks/hooks.json)`.
- Árvore do autor limpa após as rodadas.

Resultado: aprovado no head 2d1fa4fa; sem bug aberto.

## Revalidação no head caae27c4 (E58.60, escopo incremental)
Delta lido por `forge-check parecer delta` (intervalo 2d1fa4fa..caae27c4): F3 passa a recusar `monitors` e `workflows` na raiz (A18), F6 passa a quebrar linha em toda quebra do `splitlines`, o CR sozinho incluso (A17), em `bin/forge_comparar.py` e na ajuda de `bin/forge-check`; `tests/test_comparar.py` (65 testes) e specs `-12`, `-13`, `-17` (nova); `changelog.d`, proposta. Saídas em `/root/.forge-contrib/wt/qa-E5860-out/`; TMPDIR próprio; `timeout 1500` em primeiro plano.

- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 65 testes, OK.
- Mutantes, uma chamada por spec, todas rc 0, `rev=caae27c42db7`: -17 5, -12 8, -13 8 = 21 mutantes, 21 morreram, 0 sobreviventes, 0 sem veredito (CMP109 com `(erro)`: teste declarado dá erro sob o mutante e passa sem ele).
- `bin/forge-mutante --cobertura --base 821db42e` (rc 0): `rev=caae27c42db7…`; todas as condições `coberta`; uma `isenta` (`bin/forge_comparar.py:297`, teto do pool); `não coberto` só em dados (`tests/comparar/corpus.jsonl`, `tests/pesos-d4.json`). Nenhuma `isenta velha`, nenhuma sem mutante.
- Sondas por CLI em repositório meu (`qa-E5860-out/s`, corpus de 1 caso), base contra um commit que viola só o item:
  - controle `comparar HEAD HEAD`: rc 0, `aceites-novos=0`.
  - `.md` com CR sozinho antes de `hooks:`: rc 2, `nao-verificavel (F6 cabeçalho de .md fora da forma simples)`.
  - `.md` com NEL (U+0085) antes de `hooks:`: rc 2, mesma saída F6.
  - `.md` com U+2028 antes de `allowed-tools:`: rc 2, mesma saída F6.
  - `monitors/monitors.json` na raiz: rc 2, `nao-verificavel (F3 monitors/monitors.json na raiz)`.
  - CRLF legítimo no cabeçalho: rc 0 (sem falso positivo).
- Árvore do autor limpa após as rodadas.

Resultado: aprovado no head caae27c4; sem bug aberto.

## Revalidação no head bb1bac50 (E58.98, escopo incremental)
Delta lido por `forge-check parecer delta` (intervalo caae27c4..838c5a21, sem a develop; `git diff c9d69234 HEAD` separa o que veio dela): merge da develop com os pesos das duas chaves em `tests/pesos-d4.json`, par novo na guarda C-2 em `bin/forge-check`, `bin/forge-testes`, CMP102 alinhado à `RAIZ_FORA` (specs `-9` e `-15`), `docs/indice-forge.md` regenerado, `tests/test_comparar.py` (66 testes, com o teste que mata o CMP60) e `tests/test_reval_delta.py`. TMPDIR próprio; sem suíte inteira. O remoto trouxe só o parecer do review (61ffacba), por `git pull --rebase`.

- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 66 testes, OK. `test_reval_delta.py`: 10 testes, OK.
- `bin/forge-mutante tests/mutantes/v0478-ae7-comparar-9.json tests/mutantes/v0478-ae7-comparar-15.json --ids CMP60,CMP102` (rc 0, `rev=61ffacba0c37`): `CMP60 · morreu · bin/forge_comparar.py:285`; `CMP102 · morreu · bin/forge_comparar.py:54`. 0 sobreviventes.
- Vermelho (`bin/forge-testes --vermelho c9d69234 --modulos test_comparar`, rc 0): `vermelho: base=c9d69234828f head=61ffacba0c37 módulos=test_comparar (restrito por --modulos)`; `contagem: não prova (passa na base)=65; prova (asserção)=1` (`Subcomando.test_forge_check_comparar`). O teste novo `DecisaoInteira.test_reescrita_da_base_contra_recusa_do_head_nao_conta` sai "não prova (passa na base)": a base não tem `bin/forge_comparar.py` e a ferramenta não separa isso. A prova dele é o mutante CMP60 morto acima; nenhum teste cai no head.

Resultado: aprovado no head bb1bac50; sem bug aberto.
