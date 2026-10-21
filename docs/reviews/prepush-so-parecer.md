---
tipo: review
contrato: 1
pedido: prepush-so-parecer
branch: melhoria/prepush-so-parecer
commit: 6753dc7c6532e4d10bfa051277d69125f729dc50
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Code review: PREPUSH-SO-PARECER (E1.2)

Rodada 1, revisor diferente do autor (D-ETAPAS-INST). Diff lido: `10c838f..6753dc7`, 3 arquivos, 257+/1- (`.githooks/pre-push`, `changelog.d/prepush-so-parecer.md`, `tests/test_pre_push_parecer.py`), mais o `.githooks/pre-push` inteiro.

Ferramentas rodadas, em cópia própria de 6753dc7 (`git archive` em `$TMPDIR`, sem tocar o HEAD da worktree): `python3 -m unittest tests.test_pre_push_parecer -q` → `Ran 14 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; o autor registrou 1208 OK no push e o QA os refaz no head). Segurança do hook (`.githooks` é controle): parecer próprio do `security-engineer`, não refeito aqui.

## Achados
- A1 (bloqueante) .githooks/pre-push:144 · atalho aceita docs/security e docs/devops mas não roda NeutralidadeDoNucleo, que varre essas pastas: parecer com termo de stack passa no hook e a árvore vermelha vira verde (linha 149).

## Parecer
Reprovado por A1. O resto do desenho está bom e é o que a decisão do dono pede.

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
