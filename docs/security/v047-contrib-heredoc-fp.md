---
tipo: revisao-seguranca
contrato: 1
pedido: v047-contrib-heredoc-fp
branch: melhoria/v047-contrib-heredoc-fp
commit: f7e12a87a474a2e61ea2a0e621e9847c988d9ca0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-contrib-heredoc-fp (E2.105)

Parecer completo (primeiro parecer desta branch) sobre o head `f7e12a87`, base `f4b0c2ae`. A entrega afrouxa a rede D da ADR 0011 em `hooks/parecer.py`: o corpo de heredoc lido só pelo Python da entrada (`python3 -`) deixa de ser comando e de marcar a chamada, e o corpo de `sh`/`bash`/`dash` que só lê ou espera deixa de ligar a gramática com heredoc. O foco foi achar o heredoc que faz PR de verdade e passa.

## Gatilhos
`R-SEGURANCA`: mudança em hook que guarda ação crítica (merge e PR, `R-REVIEW` e `R-CONTRIB`), com afrouxamento de controle (ADR 0011, emenda v047, rótulo `afrouxa-regra`).

## Achados
- A1 (recomendado) hooks/parecer.py:176 · LANCA_PROCESSO é lista negativa (AR-3, AR-10): Python que lança gh pr merge por lançador fora dela (operator.attrgetter/methodcaller, timeit, pickle) e nome partido em literais adjacentes passa no head e era recusado na base; o python3 -c igual já passa.
- A2 (recomendado) hooks/parecer.py:238 · Correção barata: rodar LANCA_PROCESSO também sobre o texto das constantes juntadas (o ast une "sys" "tem") e pôr na lista operator, timeit, pickle, marshal, shelve, code, pdb, ou trocar por lista positiva de chamadas.

## Sondas

## Detalhe dos achados
**A1.** Sondas executadas (repositório descartável de `Fixture.montar`, hook `parecer` do head e de uma cópia `git archive f4b0c2ae`), todas com `gh pr merge 12` que roda de verdade:
- `python3 - <<'EOF'` + `import os, operator` + `operator.attrgetter("sys" "tem")(os)("gh pr merge 12")`: head rc=0, base rc=2.
- `operator.methodcaller("sys" "tem", "gh pr merge 12")(os)`: head rc=0, base rc=2.
- `import timeit` + `timeit.timeit("os.sys" "tem('gh pr merge 12')", "import os", number=1)`: head rc=0, base rc=2.
- `import pickle` + `pickle.loads(b"cos\nsystem\n(S'gh pr merge 12'\ntR.")` (no fonte, `\n` é escape, então `system` vem depois de `n`): head rc=0, base rc=2.
- Controle: `subprocess.run(["gh","pr","merge","512"])` segue rc=2 no head; `python3 -c "import os; os.system('gh pr merge 12')"` dá rc=0 no head **e na base**.

Caminho de ataque: um agente que quer contornar o hook escreve o corpo para fugir da lista. Severidade: baixa. Não é bloqueante, por proporcionalidade e pelo critério de reversão da própria emenda da ADR 0011 (linha 44): a sonda tem de rodar um comando de PR que o `python3 -c` equivalente, na mesma chamada, não rodaria. O `-c` equivalente passa em base e head (cartão N-HOOK1, X1 e X3), então não há capacidade nova. `docs/hooks.md` (seção "Heredoc a interpretador") já diz que a lista é reforço e não fronteira e que não cobre lançador fora dela. Todas as sondas exigem evasão deliberada: nenhuma forma natural (subprocess, os.system, asyncio, posix_spawnp, getattr, lista em várias linhas, concatenação) passa. O fixture correspondente existe e dá rc=2.

**A2.** Correção mínima, esforço P, dono `tech-lead` (autor do hook): em `leitores_dos_corpos`, aplicar `LANCA_PROCESSO` ao corpo e também a `" ".join(constantes)`, o que fecha o nome partido em literais adjacentes, e pôr na lista os nomes `operator`, `timeit`, `pickle`, `marshal`, `shelve`, `code`, `pdb` e `attrgetter`/`methodcaller`. Alternativa estrutural, na linha da ADR 0011 (gramática positiva): o corpo de Python só sai da regra se a árvore `ast` tiver só chamadas de uma lista positiva (`print`, métodos de `str`, `open` só para leitura, `json`, `re`). Sondas acima viram fixtures `heredoc-interpretador-*-bloqueia`.

Outras dimensões conferidas, sem achado: dono com caminho, atribuição (`PATH=`, `env PATH=`), script, pipe, tipos mistos; lançadores (`timeout`, `env`); `git` e atribuição solta fora dos corpos (`chamada_muda_o_corpo`); `<<` não simples (`heredocs_simples`); corpo que o `ast` não lê (falha fechada); corpo de `sh` que só lê segue conferido como comando no nível 1 (`hooks/parecer.py:1013`); M3 com `gravado` e `sh x.sh` segue recusando. Chamada direta à API de merge (`urllib`, `http.client`, `curl -X PUT .../pulls/12/merge`) dá rc=0 em base e head: lacuna anterior, fora do delta (vira cartão, ADR 0011 item 3).

Testes do item rodados no head: `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_interpretador_libera_e_bloqueia` e `test_corpus_texto_passa_e_barra`, OK (2 testes). Ainda não há PR nem CI nesta branch. A suíte inteira é portão do CI do PR (`R-REVIEW`), e este parecer não a substitui.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. O afrouxamento é decisão do dono registrada na emenda v047 da ADR 0011 (escopo E4). Ferramentas: o hook rodado localmente com as sondas acima. `gitleaks`, Semgrep, `zizmor` e `actionlint` não estão no PATH (lacuna; a entrega não toca workflow nem segredo).
