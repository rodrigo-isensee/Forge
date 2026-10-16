---
tipo: review
contrato: 1
pedido: conferente-k2
branch: melhoria/conferente-k2
commit: ef3ef4d9bd136d0d1b67c4245aa2b401ca4d94c0
parecer: aprovado
revisor: forge:tech-lead (independente)
data: 2026-10-16
---
# Code review independente: conferente confiável, fatia K2

Escopo: `git diff origin/develop...HEAD` (origin/develop `4922609`, já contida na branch pelo merge `ef3ef4d`, sem conflito; implementação até `6d3f41b`, Base-sha `a7246d4`). São 18 arquivos, +879/−11. Conferi o diff contra o "Entregar" do brief da K2 (`~/.forge-contrib/docs/briefs/k2-tech-lead-3.md`, itens 1 a 8) e contra o pedido `k2-e-processo` (E1 e "Decisões técnicas do time", 2026-10-16 ~05h). Não escrevi esta branch.

## Parecer: **aprovado**
Todos os itens do "Entregar" foram entregues. A saída do `forge-check brief` é determinística, `tests/config.json` só recebeu acréscimos e `hooks/conformidade.json` só ganhou `"forge-check brief"`. Os três achados abaixo são recomendados e nenhum bloqueia. Eles voltam ao autor em outra delegação (D-ETAPAS = A).

## Achados
| # | Arquivo:linha | Problema | Sugestão | Severidade |
|---|---|---|---|---|
| 1 | `bin/forge-check:1649` | `comando_do_conferente` recusa `(`, `$`, `{`, `#`, `*` e `?` também dentro de aspas simples. A gramática do conferente (`agents/conferente.md:27`) só recusa `$(` e crase entre aspas. Por isso `grep -nE '^(parecer\|commit):' a.md` e `grep -n 'v1$' src/app.js`, que o conferente pode rodar, saem `verificador: autor`. Conferido: as duas chamadas retornam `False`. Isso não reprova nada, só rotula errado e manda ao QA uma prova que o conferente poderia conferir. | Antes de testar os sinais, tirar o conteúdo das aspas simples, recusando só `$(` e crase nelas. Acrescentar esses dois casos a `test_verificador_do_cmd_segue_a_lista_do_conferente`. | recomendado |
| 2 | `bin/forge-check:1660` e `tests/test_forge.py:2565` | `bin/forge-check ...` e `./grep ...` saem como comandos do conferente, com `True`. Mas o hook recusa programa com caminho (`hooks/conformidade.py:723`, `"/" in prog`), e o conferente lista o `forge-check` "pelo nome, sem caminho" (`agents/conferente.md:24`). Um PQ escrito assim sai `verificador: conferente`, e o conferente recebe recusa do hook (`não verificável`). O teste fixa o comportamento divergente. | Aceitar só o nome, sem caminho, como faz o hook. No teste, mover `bin/forge-check brief a.md --pedido p` para a lista do `assertFalse` e acrescentar `./grep x a`. | recomendado |
| 3 | `hooks/conformidade.json:77` (sem teste) | O acréscimo de `"forge-check brief"` não tem fixture de hook que prove que o conferente passou a poder rodar o comando. Os casos de `forge-check` em `tests/hooks/conformidade/conferente-*` cobrem só `forge-check pr`. A decisão técnica do time diz que, sem o acréscimo, o hook recusa. Falta o teste que mostre que agora libera e que `--pedido=-...` continua bloqueado. | Acrescentar `conferente-forge-check-brief-libera.json` (`forge-check brief docs/briefs/p1-dev-1.md --pedido p1 --destino forge:dev`) e um caso `... --pedido=--output=x` que bloqueia. | recomendado |

Informativo, não é achado do diff: os briefs reais deste pedido têm nomes fora do padrão `docs/briefs/<pedido>-<destino>-<n>.md` (por exemplo, `k2-review-tl.md`). Com `--destino`, o comando reprova esses briefs com `forma: Arquivo fora do padrão docs/briefs/k2-e-processo-tech-lead-<n>.md`, como deve. Depois do merge, o Jarvis precisa gravar os briefs com esse nome.

## Entregar do brief, item a item
1. **`forge-check brief` (C2, C4).**
   - Subcomando entregue em `bin/forge-check:1519-1877`, com a documentação no cabeçalho de uso.
   - Classe `ConferirBrief` com 25 testes. Estão lá os seis fixtures com os nomes pedidos e o `pedido.md` sintético.
   - O comando e o uso dele estão nos modos brief e entrega (`agents/conferente.md:25`, `:42` e `:68`).
   - Em `hooks/conformidade.json` só entrou o acréscimo.
2. **`brief gerar` (PA-2).**
   - Só lê. O único git que roda é `rev-parse` e ele só imprime.
   - Copia as `DECISÃO DO DONO` literalmente, lista as etapas de outro papel (no formato que o `brief` reconhece por trecho literal), a marca de corte e o formato das provas.
   - O que falta decidir fica em `PREENCHER`, e o `brief` reprova enquanto houver algum.
   - Testado: decisões literais, etapa do próprio papel fora do Fora do escopo, duas execuções com a mesma saída e pedido ilegível saindo com 2.
3. **Passada única.** A frase "todos os achados" está em `agents/conferente.md`, `docs/regras/R-BRIEF.md` e `agents/jarvis.md`, com invariante e com o teste `test_conferente_lista_o_comando_e_a_passada_unica`.
4. **S-3.** O checklist de autoconferência está em `R-BRIEF.md` (cinco pontos: decisões literais, marcas e etapas, vocabulário de `espera:`, hashes completos e regras citadas pelo texto delas) e resumido em `agents/jarvis.md`.
5. **S-6.**
   - `FragmentoTemONomeDaBranch` cobre três casos: nome certo e errado pela função pura, `forge-changelog novo` gravando com o nome da branch, e os fragmentos novos desta branch contra `origin/develop`.
   - Esse último pula fora de `melhoria/*` e quando não há `origin/develop`.
   - O `slug_da_branch` foi extraído sem mudar o comportamento de `novo`.
6. **Achados da K1.**
   - B1: hash completo na linha `arquivo:`, `Brief-sha256:` na entrega e caminho conferido com `--destino`.
   - B2: `forma: sem PQ que o conferente confira` sai do comando, e "não roda" virou "fora da lista de comandos do conferente" em `R-PROVA.md:11`.
   - B3: entraram os sete trechos pedidos (`etapa do papel do destino que falta` já existia).
   - B4: `tests/config.json` nunca é anexo, e o comando agora usa `--no-renames`.
   - B5: `escopo: base fora do fluxo`.
   - I1: `forma: modo ausente`.
   - I2: o `aviso:` de espera fraca e `rc=0 e <espera>`.
   - BUG-K1-1: invariante `existe só na entrega`.
7. **Invariantes e fragmento.**
   - `git diff --numstat` de `tests/config.json` dá `31 0`, ou seja, só acréscimo.
   - Rodei cada regex nova sobre o arquivo dela: cada uma casa exatamente uma vez.
   - O fragmento é `changelog.d/conferente-k2.md` e não toca `CHANGELOG.md` nem `plugin.json`.
8. **Commits.** São cinco, pequenos, em Conventional Commits em português (`test`, `feat`, `feat(hooks)`, `docs`), com trailers. O merge da develop está separado em `ef3ef4d`.

## Conferido e certo
- **Determinismo.** A saída depende só do texto do brief, do pedido e do nome do arquivo, sem hora nem ordem de dicionário (as seções e IDs são percorridos ordenados). `test_saida_igual_nas_tres_execucoes` cobre isso. Rodei o comando duas vezes sobre o brief real deste review e o md5 da saída foi o mesmo (`a771d518…`).
- **Clean code.** As funções são pequenas e com nome claro (`secoes_por`, `itens_de`, `ler_pedido_brief`, `conferir_pq`, `conferir_corte`). O erro de leitura sai com código 2 e mensagem com o caminho. Não há código morto nem depuração esquecida.
- **Os testes cobrem os casos dos fixtures e as bordas:**
  - cada campo da marca de corte;
  - a marca sem a frase literal;
  - trecho citado fora do pedido;
  - citação parecida (`E10`, `E1.2`, sem parênteses);
  - etapa do papel do destino;
  - seção ausente;
  - `PREENCHER`;
  - tipo de prova desconhecido;
  - espera combinada e espera fraca;
  - pedido por id via `--raiz`.
- **R-NEUTRO.** Os fixtures são sintéticos (`pedido-sintetico`, `dev-exemplo`, `revisor`, `qa`), e o texto novo não traz nome de projeto nem stack. `tests.test_forge.Neutralidade` e `RegrasInviolaveis` passaram (`Ran 3 tests` / `OK`).
- **R-CUSTO.** Não há rede nem serviço pago. O `gerar` usa só `git rev-parse`, que é local.

## Ferramentas (citadas, não refeitas)
- **Suíte completa:** não rodei, por R-TETO e porque a segurança roda em paralelo na mesma worktree. O autor a rodou (685 OK) e o QA roda de novo. Aqui rodei só as classes novas: `python3 -m unittest tests.test_forge.ConferirBrief tests.test_changelog.FragmentoTemONomeDaBranch` deu `Ran 28 tests in 2.512s` / `OK`.
- **`scripts/validar-plugin.sh`:** fica com o QA (`R-QA`).
- **Segurança:** o diff toca `bin/forge-check` e `hooks/conformidade.json`, e o parecer próprio é do `security-engineer` (`docs/security/conferente-k2.md`, E3.2). Este review não o refaz. O achado 3 (teste do hook) também interessa a ele.
