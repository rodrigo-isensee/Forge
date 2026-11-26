---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 07a1bf5c6420ea060b517927cf06cb8090e7bb6f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E7.61, #888, revalidação por delta, 6ª volta)

Gatilhos: hook de bloqueio (`hooks/_comum.py`, `hooks/conformidade.py`), R-REVIEW, R-CONFORMIDADE, R-CONTRIB, R-QA (mutantes).

- ci: 07a1bf5c6420ea060b517927cf06cb8090e7bb6f verde

## Resumo
- Delta lido: `git diff 22a57afc..07a1bf5c` e `forge-check parecer delta`. O delta tem os três pareceres da volta anterior (`bdc4fdce`, `e922db75`, `ec272bb6`), o merge da develop `39d6f4f4` (entrou o #878, `22ceb2c8`) e o merge `07a1bf5c`, que só junta o parecer de review.
- **Resolução do conflito:** `git show --remerge-diff 39d6f4f4` mostra só `docs/hooks-fixtures.md`, regerado (3603 fixtures, `conformidade` 2725). A conta fecha: 3587 da base, mais 7 do item, mais 9 do #878. `scripts/indice-fixtures.py --conferir` dá "em dia". O `07a1bf5c` não tem resolução (`--cc` vazio).
- **A develop entrou igual:** `git diff 020e4af7 22ceb2c8` (o #878) e `git diff e922db75 39d6f4f4` têm os mesmos 31 arquivos (+1246/-6). Fora o índice, as linhas `+`/`-` são idênticas, inclusive em `hooks/conformidade.py`, `hooks/conformidade.json`, `tests/test_hooks.py`, `tests/catraca.py` e `bin/forge-testes`. `hooks/conformidade.py` e `tests/test_hooks.py` juntaram sem conflito. As partes do item (`especial_no_git` em `hooks/conformidade.py:1854` e `:2596`) e do #878 (`ultima_raiz` em `:1386`, `forge_check_publica` em `:2559` e `:2658`) ficam em funções e ramos separados. Nenhuma lê o estado da outra.
- **O teste que a catraca aponta:** `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada` vem do item, não da junção.
  - O corpo do teste é igual em `22a57afc` e em `07a1bf5c`. O valor esperado (`tests/test_hooks.py:1311`, 4.0 → 3.5) mudou no `1d6692f5` (E7.32), junto com o `sleep 4` → `sleep 3.5` do fixture `parecer/v0455-merge-com-git-lento-decide-no-prazo-longo.json` e com `PRAZO_DO_MERGE_S` 8.0 → 7.5 (`hooks/_comum.py:2839`).
  - O teste continua conferindo que o sono lido do fixture é o do fixture. Para a segurança, é neutro.
  - A catraca só avisa ("não barra na primeira entrega"). Esse ponto já estava aprovado nas voltas anteriores.
- **O que aperta:** nada que a junção tenha escrito. O que aperta neste delta veio do #878 e já foi revisado lá:
  - a barreira R-CONTRIB de `forge-check parecer publicar` com alvo no Forge, vindo da sessão de outro projeto;
  - as quatro regras de dono para `.forge/pareceres/*/` em `hooks/conformidade.json`;
  - `bin/forge_pareceres.py` nos `PROTEGIDOS` da catraca.
- **O que é neutro:** a resolução (índice gerado), o merge do parecer, o teste novo `test_fixtures_do_publicar` (vem do #878 e só acrescenta) e a troca do valor esperado acima.
- **O que afrouxa:** nada. O afrouxamento na margem das travas de recurso, aceito pelo dono em 25/11 21:15, segue como em `ecb13af6`, sem mudança.
- **Achados anteriores:** A3, A6 e A7 continuam resolvidos (`4ab16b74`). A isenção de `:2875(base)` continua atendida (`ecb13af6`).
- **Provas locais** no head `07a1bf5c`:
  - o teste apontado, `test_fixtures_do_publicar` e `tests.test_forge_pareceres`: 37 testes OK;
  - mutantes `tests/mutantes/v0481-g2-1-publicar*.json` (seis specs, os que guardam o trecho de `hooks/conformidade.py` que a junção tocou): M1 a M37, todos mortos.
- **CI** no head (run 45815173541, `pull_request`, base da PR já em `604f3069`):
  - verdes: as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `árvore já provada na develop`, `teto de pulados` e `bateria (python 3.14)`;
  - vermelho `bateria (pareceres)`: o log diz R-REVIEW, porque o parecer de review ficou desatualizado pelo índice regerado. Os pareceres desta volta resolvem isso;
  - vermelho `bateria`: o agregador, que só cai por `PARECERES: failure`;
  - vermelho `catraca` (run 45815173436): o log diz R-CONFORMIDADE em `hooks/_comum.py` e `hooks/conformidade.py`, que pedem o rótulo `afrouxa-regra` do dono depois do último push. É um passo do dono, não um defeito.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo.

Ferramentas: `forge-check parecer delta`, `git show --remerge-diff`, `git diff` com as linhas `+`/`-` comparadas, `scripts/indice-fixtures.py --conferir`, `unittest`, `bin/forge-mutante` e `gh run view` (logs dos jobs). Não usei nada externo. O delta não traz dependência nem segredo.
