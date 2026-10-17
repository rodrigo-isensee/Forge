---
tipo: revisao-seguranca
contrato: 1
pedido: pa-4
branch: melhoria/pa-4-parecer-commitado
commit: 54bfcf9d56fb9f7f1f18c4ca9edca84947f9703f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-16
---
# Review de segurança: pa-4

Escopo: `git diff b38cd283fcb521db573815170d03a435f880e619...4a28e23c1c4f05ba7e0270d5acf6364b18b21f3c`, 8 arquivos (+55); foco em `bin/forge-check` (`cmd_pr`, chamado pelo hook `hooks/parecer.py:171` no PR, no `gh pr ready` e no merge). Ameaças consideradas: parecer não commitado ou de outro commit passar pelo portão; falha de git abrir o portão por engano ou fechá-lo para sempre; `--ref` passar a ler a árvore de trabalho; a instrução nova dar ao security-engineer escrita fora de `docs/security/` ou em `docs/security/aceites/`.

## Gatilhos
`R-SEGURANCA`: muda controle do Forge (o portão de parecer, `forge-check pr`, usado pelo hook de parecer).

## Resumo
**Aprovado.** A mudança só acrescenta uma recusa (nenhum caminho que antes bloqueava passa a liberar) e fecha uma lacuna real: com `ref` nulo (PR da branch atual, `hooks/parecer.py:189`), `documentos()` lê o parecer do disco (`bin/forge-check:180`), então um parecer só na árvore de trabalho valia. Um achado baixo (a conferência por `git status` pode ser contornada por `skip-worktree`/`assume-unchanged`, comprovado em repositório temporário) e um informativo; nenhum é regressão. `python3 -m unittest tests.test_forge.ForgeCheck`: 42 testes, OK.

## Conferido
- **Parecer não commitado é recusado.** `bin/forge-check:506-508`: com `ref` nulo, o parecer escolhido (`:504`) passa por `parecer_commitado` (`:477-485`): ausente no HEAD (novo ou só no índice) → recusa (`:482-483`); presente no HEAD e alterado no disco ou no índice → recusa (`:484-485`). Sondagem: arquivo novo, editado depois do commit e só no índice dão `False`; testes `test_pr_parecer_so_na_arvore_de_trabalho_falha` cobrem os três.
- **Parecer de outro commit continua recusado.** A ligação `commit:` → HEAD segue em `commit_vale` (`:520-523`), intacta; o commit do próprio parecer cai em `LIVRES` (`:59`, inclui `docs/security/`), logo commitar o parecer não o invalida e não abre brecha para código (só caminhos de `LIVRES` são tolerados depois do commit revisado).
- **Falha de git não abre o portão.** Sem HEAD (`:481`) a função devolve `True`, mas o portão continua fechado pelo `commit_vale` (`rev-parse` do `commit:` falha → "commit não existe no repositório", `:367-369`; sem `commit:` válido, `validar_documento` acusa). `TimeoutExpired` do `git()` (`:282`) sobe; no hook, comando com marcador crítico (`pr create|merge|ready`, `hooks/parecer.py:24`) bloqueia. Não há estado persistente: a recusa some assim que o parecer é commitado, portanto não fecha para sempre.
- **`--ref` lê só do git.** A conferência nova só roda com `ref is None` (`:506`); com `ref`, `documentos()` usa `ls-tree`/`show` (`:174`, `:180`) e o aceite usa `git show` (`:450`), sem mudança. Teste `test_pr_com_ref_nao_olha_a_arvore_de_trabalho`.
- **Sem injeção.** `rel` é `pasta/nome` de um `glob` (`:172`, `:179`), passado como argumento de lista ao `git -C`; começa por `docs/`, então não aciona magia de pathspec; curinga no nome só alarga o `status` (falha fechada).
- **Instrução do security-engineer não dá escrita nova.** `agents/security-engineer.md:15` restringe o commit a `docs/security/` (parecer e modelo de ameaças) e exclui `docs/security/aceites/` e código; `hooks/conformidade.json` não muda no diff e segue negando `docs/security/aceites/` a todos (`:43`) e dando `docs/security/` só ao `seguranca` (`:44`). Os outros três papéis (`agents/tech-lead.md:17`, `agents/qa-engineer.md:21`, `agents/devops-engineer.md:18`) commitam só o próprio arquivo, com `git add` explícito; nenhum `--force`/`--no-verify`.
- **Invariantes só por acréscimo** (`tests/config.json`, 6 linhas novas, nenhuma removida). **Sem custo** (`R-CUSTO`): só `git` local.

## Achados
### B-PA4-1. `skip-worktree`/`assume-unchanged` escondem do `git status` o parecer editado (baixa)
- **Evidência:** `bin/forge-check:484-485` decide por `git status --porcelain`, mas o texto julgado é o do disco (`:180`, `:504`). Nenhum hook trata `git update-index` (busca em `hooks/` e `bin/` sem ocorrência).
- **Caminho:** um agente da sessão (por engano ou para destravar o portão) faz `git update-index --skip-worktree docs/qa/<pedido>.md` (ou `--assume-unchanged`) e reescreve no disco o parecer commitado `reprovado` como `aprovado`; o `status` fica vazio, `parecer_commitado` devolve `True` e o `forge-check pr` aprova com o texto do disco, enquanto o commit enviado traz `reprovado`. Reproduzido em repositório temporário: editado → `False`; editado + `skip-worktree` → `True`; editado + `assume-unchanged` → `True`. Exige ação deliberada dentro da sessão e não piora o estado anterior (antes não havia conferência), por isso baixa. O mesmo vale se o `status` falhar com HEAD legível (`bool(cod)` em `:485` libera).
- **Sugestão:** comparar conteúdo em vez de estado: `cod, salvo = git(raiz, "show", f"HEAD:{rel}", bruto=True)` e devolver `not cod and salvo == (raiz / rel).read_bytes()`; elimina o `status`, cobre índice, `skip-worktree` e `assume-unchanged` e falha fechada. Teste: o caso `skip-worktree` acima.
- **Esforço:** P · **Dono:** tech-lead (autor).

### I-PA4-1. Parecer apagado só no disco não é percebido (informativa)
- **Evidência:** `bin/forge-check:172` (lista do disco) e `:504` (escolhe o mais recente entre os do disco).
- **Caminho:** só quando o pedido tem mais de um arquivo de parecer na mesma pasta: o mais recente, `reprovado` e commitado, é removido do disco sem commit; o mais antigo, `aprovado` e commitado, passa a ser o escolhido e a conferência nova não vê diferença. O convencional é um arquivo por pedido (`docs/<pasta>/<pedido>.md`), por isso só registro.
- **Sugestão (opcional):** com `ref` nulo, ler a lista de pareceres de `HEAD` (`documentos(raiz, tipo, "HEAD")`) e exigir que o escolhido no disco seja o mesmo.
- **Esforço:** P · **Dono:** tech-lead (opcional).

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum. B-PA4-1 corrigido na volta do autor (ver abaixo); I-PA4-1 segue opcional.
- Ferramentas: revisão estática do diff; sondagem de `parecer_commitado` em repositório temporário (`$TMPDIR`); `tests.test_forge.ForgeCheck`. Lacuna: `gitleaks`, `semgrep` e afins não foram usados (nada instalado por mim); o diff não traz segredo nem toca workflow, conferido por leitura.

## Revalidação após a volta do autor
Escopo: `git diff 4a28e23c1c4f05ba7e0270d5acf6364b18b21f3c..7424d5c2a9ed7c74b62cbc19d3964f8a492d40d1 -- bin/ tests/ agents/ changelog.d/` (da2f537 e 7424d5c). **Aprovado; B-PA4-1 corrigido, sem desvio novo.**
- **B-PA4-1 corrigido.** `parecer_commitado` (`bin/forge-check:478-485`) não usa mais `git status`: compara os bytes de `git show HEAD:<rel>` (`bruto=True`, `:284-285`) com `(raiz / rel).read_bytes()`, o mesmo arquivo cujo texto o portão julga (`:504`). `--skip-worktree` e `--assume-unchanged` só mexem no índice, então não alteram a comparação. Falha do `git show` com HEAD legível dá `cod != 0` e devolve `False` (recusa): fecha, não libera. Sem HEAD continua `True`, coberto pelo `commit_vale` como antes.
- **Teste.** `tests/test_forge.py:1647-1659` (`test_pr_parecer_editado_nao_escapa_por_skip_worktree_nem_assume_unchanged`) edita o parecer commitado sob cada marca e espera a recusa; depois desfaz e espera aprovação. Mutação: com o `bin/forge-check` de 4a28e23 (cópia em `$TMPDIR`) o teste falha; com o de 7424d5c passa. `python3 -m unittest tests.test_forge -q`: 237 testes, OK.
- **Sem desvio novo.** O resto da volta é texto: ajuda do `pr` e do `--ref` (`bin/forge-check:33`, `:2056`) e a retirada do rótulo de cartão interno nos quatro agentes; a regra (só o arquivo do parecer, `git add` explícito, e para o security-engineer só `docs/security/` fora de `docs/security/aceites/`) ficou intacta. `tests/config.json` e `changelog.d/` não mudaram. Comparação por bytes não passa por filtros de checkout; num clone com `core.autocrlf` ou filtro `smudge` no parecer, o efeito é recusa indevida (falha fechada), não liberação: só registro.

## Revalidação após a segunda volta do autor (54bfcf9)
Escopo: `git diff 7424d5c..54bfcf9 -- bin/ tests/ agents/ changelog.d/`. **Aprovado, sem desvio.** A mudança é só texto de ajuda (`bin/forge-check:2054`, `help=` do subcomando `pr`) e um teste novo (`tests/test_forge.py:1661`, `test_ajuda_geral_cita_parecer_commitado_no_pr`); a lógica do portão (`parecer_commitado`, `commit_vale`) não foi tocada; `agents/` e `changelog.d/` sem alteração. `python3 -m unittest tests.test_forge -q`: 238 testes, OK.
