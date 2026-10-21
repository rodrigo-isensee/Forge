---
tipo: review
contrato: 1
pedido: prepush-so-parecer
branch: melhoria/prepush-so-parecer
commit: 862bf19cb7367460eef1c6d1ec0e431e49ea53d5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Code review: PREPUSH-SO-PARECER (E1.2)

Rodada 1, revisor diferente do autor (D-ETAPAS-INST). Diff lido: `10c838f..6753dc7`, 3 arquivos, 257+/1- (`.githooks/pre-push`, `changelog.d/prepush-so-parecer.md`, `tests/test_pre_push_parecer.py`), mais o `.githooks/pre-push` inteiro.

Ferramentas rodadas, em cópia própria de 6753dc7 (`git archive` em `$TMPDIR`, sem tocar o HEAD da worktree): `python3 -m unittest tests.test_pre_push_parecer -q` → `Ran 14 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o autor registrou 1208 OK no push e o QA os refaz no head). Segurança do hook (`.githooks` é controle): parecer próprio do `security-engineer`, não refeito aqui.

## Achados

## Parecer
Rodada 1: reprovado por A1 (texto abaixo, mantido como histórico). Volta 1: aprovado, ver "## Volta 1". Volta 2: aprovado, ver "## Volta 2". O resto do desenho está bom e é o que a decisão do dono pede.

A1, evidência (sonda em `$TMPDIR`, cópia de 6753dc7): com `docs/security/sonda.md` citando `npm audit` e `pip-audit` e `docs/devops/sonda.md` citando `Node`, as três classes do hook dão `OK`, e `python3 -m unittest tests.test_forge.NeutralidadeDoNucleo` dá `FAIL` nos dois arquivos (`stack no núcleo (npm)`, `(Node)`, `pip-audit`). Motivo: em `tests/config.json`, `neutralidade_nucleo.ignorar` lista só `docs/adr/`, `docs/reviews/` e `docs/qa/`. O comentário da linha 114 diz que as classes são "as mesmas que o gate do CI usa", mas o gate do CI (`.github/workflows/ci.yml`, passo Gate) só pula para `docs/(reviews|qa)/`; o hook estendeu o atalho a duas pastas sem estender as classes. Parecer de segurança e de devops citar ferramenta de stack é o caso comum, não de borda. A anotação da linha 149 roda também depois do caminho curto, então a árvore que falharia a suíte entra no arquivo `.verde` e os próximos pushes de parecer em cima dela seguem curtos. O CI pega no PR (para essas pastas ele roda a bateria pesada), mas o hook prometeu falha fechada e aqui ela é aberta. Mesma família, menor: `tests/test_volta_por_delta.py` (`test_parecer_escrito_pelo_modelo_passa_no_gerar_volta`) lê `docs/security/_modelo.md`, e um push que só mexe nesse modelo também cairia no atalho.

Sugestão para a volta (o autor escolhe): acrescentar `tests.test_forge.NeutralidadeDoNucleo` às classes do caminho curto (é barata, mesma varredura de arquivos) e mandar à suíte inteira todo arquivo de nome `_*` nas quatro pastas (modelos, não pareceres); teste novo no `tests/test_pre_push_parecer.py` com a suíte mínima ganhando uma classe `NeutralidadeDoNucleo` e um caso que prove que ela roda no push só de parecer em `docs/security/`. Ajustar o comentário da linha 114 para não dizer que é o conjunto do gate do CI (ou dizer em que ele difere).

O que foi lido e está certo (não precisa reler na volta):
- Falha fechada nas condições: uma ref só, `refs/heads/*`, SHAs hexadecimais e não zerados (ref nova e exclusão de ref vão à suíte), HEAD igual ao commit enviado, árvore limpa inclusive não rastreados, árvore do remoto anotada, diff ilegível vai à suíte (`|| return 1`), delta vazio também (a linha vazia não casa com o `case`). `--no-renames` faz renomeação de fora para dentro das quatro pastas listar a origem, que vai à suíte; exclusão fora das pastas idem. A prova é por árvore (conteúdo), não por commit, então trocar de branch ou worktree com a mesma árvore não engana.
- A leitura e a escrita do `.verde` acontecem com a trava do R-TETO segura, então dois pushes não disputam o arquivo; escrita por `.novo` + `mv`, `umask 077`, recusa de link e de dono alheio; histórico limitado a 200 linhas.
- Testes: 14 casos reais (o hook de verdade num repositório descartável, suíte mínima que marca o que rodou), cobrindo as quatro pastas, cadeia de pareceres, misto, caminho fora (incluindo `docs/reviews_x.md`), prova ausente, árvore não anotada, ref nova, árvore suja, HEAD diferente, suíte vermelha não anota, mudança em `tests/`, várias refs e prova por link. Determinísticos, sem hora nem rede.
- Fragmento `changelog.d/prepush-so-parecer.md` presente, `CHANGELOG.md` e versão intocados. Commit único, Conventional Commits em português. Nada de custo (R-CUSTO) nem de projeto (R-NEUTRO).

Recomendações (não bloqueiam):
- `.githooks/pre-push:115`: o comentário diz que a árvore é anotada "depois de cada suíte verde", mas a anotação roda também depois do caminho curto; dizer isso, para quem ler saber que a prova é transitiva.
- `.githooks/pre-push:149`: `git status` é chamado duas vezes no caminho curto (129 e 149); custo baixo, pode ficar.

## Volta 1
Revalidação por delta. `forge-check delta --parecer docs/reviews/prepush-so-parecer.md` listou `6753dc7..441ae27`: `.githooks/pre-push` 117-122, 141, 150, 154-157; `changelog.d/prepush-so-parecer.md` 2; `tests/test_pre_push_parecer.py` 34-39, 44, 192-228. Lido só isso, mais o comentário vizinho (114-116); o resto do hook e dos testes ficou como "já lido" na rodada 1.

Ferramentas, em cópia própria de 441ae27 (`git archive` em `$TMPDIR`): `python3 -m unittest tests.test_pre_push_parecer -q` → `Ran 17 tests ... OK`; as quatro classes do caminho curto sobre a árvore real → `OK`; a mesma sonda da rodada 1 (`docs/security/sonda.md` com `npm audit` e `Node`) agora cai em `NeutralidadeDoNucleo` → `FAILED (failures=2)`, que é a classe que o caminho curto passou a rodar. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o pre-push deste envio e o QA os rodam).

- A1 resolvido: `tests.test_forge.NeutralidadeDoNucleo` entrou no caminho curto (linha 150), e o teste `test_termo_de_stack_em_parecer_de_seguranca_e_barrado_no_caminho_curto` prova que ela roda, que o push é barrado e que a árvore vermelha não vira prova.
- R2 da segurança, pela decisão do dono (R2 → "A"): a linha 141 manda à suíte inteira `*/_*` (modelos das quatro pastas), `docs/security/ameacas/*` e `docs/security/aceites/*`, e vem antes do padrão das quatro pastas, então ganha. O padrão exige `/_`, não pega `a_b.md`. Coberto por `test_modelo_e_pastas_de_controle_rodam_a_suite_inteira` (cinco casos, com subTest).
- R1 da segurança: a árvore anotada passa a ser a do início (linhas 121-122 e 154-157), com a árvore de trabalho limpa no início e no fim. `test_prova_grava_a_arvore_do_inicio_da_suite` (a suíte faz um commit no meio) prova que a do fim não entra. No caminho curto a árvore do início é a do commit enviado (HEAD igual a `unico_local`, já conferido), então a cadeia continua certa.

Suposição do autor (a prova só grava se a árvore estava limpa no início e no fim): é suficiente para o caso testado e mais segura que a rodada anterior, mas não fecha tudo. Limpa no início e no fim não garante que a árvore não mudou no meio: um `merge --ff-only` de outro revisor na worktree compartilhada durante os ~5 min deixa a árvore limpa no fim, e a suíte leu parte dos arquivos novos, ou seja, testou uma mistura e anota a do início. Não bloqueia: a árvore do início só vira prova se a mistura passou, o delta que a usa depois ainda precisa ser só de pareceres, e o CI repete tudo. Recomendação abaixo.

Recomendações (não bloqueiam):
- `.githooks/pre-push:156`: anotar só se, além de limpa, `HEAD^{tree}` no fim for igual a `arvore_inicio` (o que a R1 da segurança propôs); uma comparação, e o teste do commit no meio passaria a afirmar que nenhuma das duas árvores entra.
- `.githooks/pre-push:115`: o comentário ainda diz que as classes são "as mesmas que o gate do CI usa"; o gate do CI pula só para `docs/(reviews|qa)/` (`.github/workflows/ci.yml:70`) e o hook agora roda quatro classes. Dizer em que difere (repete a recomendação da rodada 1).
- Changelog atualizado e coerente com o comportamento; commit único da volta, Conventional Commits em português; nada de custo (R-CUSTO) nem de projeto (R-NEUTRO).

## Volta 2
Revalidação por delta, `4824b52..862bf19`: `.githooks/pre-push` (comentário 113-119, linha 142 da checagem de exclusão, 154-157), `changelog.d/prepush-so-parecer.md` 2 e `tests/test_pre_push_parecer.py` (`verde_em`, teste do commit no meio, apagar e renomear). Lido só isso; o resto do hook e dos testes ficou como "já lido" nas voltas anteriores.

Ferramentas, em cópia própria de 862bf19 (`git archive` em `$TMPDIR`, caminho fundo): `python3 -m unittest tests.test_pre_push_parecer -q` → `Ran 19 tests ... OK`; `bash -n .githooks/pre-push` → ok. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o pre-push deste envio e o QA os rodam).

- A1 do QA resolvido: `git diff --diff-filter=D --name-only --no-renames` não vazio manda à suíte inteira; como `--no-renames` mostra a renomeação como D mais A, apagar e renomear caem na mesma checagem, antes de o delta ser percorrido. Os testes novos apagam e renomeiam um parecer sobre árvore com prova real (`verde_em`, ref nova → suíte inteira grava a prova) e afirmam que a suíte inteira rodou.
- Recomendação da volta 1 sobre a árvore do fim aceita: a prova só grava se `HEAD^{tree}` no fim for igual a `arvore_inicio`, além da árvore limpa nos dois momentos (linha 155). O teste do commit no meio passa a afirmar que nenhuma das duas árvores entra. Fecha também o caso do `merge --ff-only` de outro revisor durante a suíte.
- Recomendação do comentário aceita: o texto agora diz que o gate do CI usa um subconjunto próprio e que a classe de neutralidade entra porque varre `docs/security` e `docs/devops`. A observação de que a anotação roda também depois do caminho curto continua só implícita; não bloqueia.
- Changelog coerente com o comportamento (exclusão, renomeação e prova só com árvore estável); commit único da volta, Conventional Commits em português; nada de custo (R-CUSTO) nem de projeto (R-NEUTRO).

Parecer da volta 2: aprovado, sem bloqueantes. A condição nova do caminho curto só vale quando todo arquivo enviado é parecer nas quatro pastas, nada foi apagado ou renomeado, não é modelo nem pasta de controle, e a prova da árvore do remoto existe.
