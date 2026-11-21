---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: 7a739fca7bed5df9a09bba96ce6b8fca799f906e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E63.14, revalidação da trilha CONFORMIDADE-SEGURANCA do `hooks/conformidade.py`, head 7a739fca)

Revalidação (H3, `R-REVIEW`) do parecer aprovado no head 0f4facab (commit 94e5fcc1). Li só o delta de
`forge-check parecer delta docs/reviews/v0479-conformidade-trilha.md`: intervalo `0f4facab..7a739fca`, domínio "código e
testes": `hooks/conformidade.py` (+32/-5), `docs/hooks.md`, `docs/hooks-fixtures.md`, o fragmento do changelog, 11 fixtures
`cpb-*` novas, os mutantes `-10` (ajuste) e `-13` (novo, W1 a W8) e a prova do custo do corpus. Fora desse domínio nada foi
relido.

## O que li no delta
- A16 da segurança: `CAMINHO_TROCADO_NA_LINHA` (`hooks/conformidade.py:3823`) reconhece o nome `HOME` fora de `$HOME` e
  `${HOME}`, `BASH_ENV`, `ENV`, `source`, o ponto como programa, `ln`, `link`, `mv`, `install`, `rename` e `cp -s|-l`.
  `sem_copia_de_wt` devolve o texto intacto quando a linha casa (a exceção da cópia de `wt/` some) e passa a contar o `$`
  do texto de antes da troca (`:3846`), o que fecha o `$` dentro do caminho lido como cópia.
- A17: `GuardaDaProva.bash` (`:3879`), só no nível 0 e para o papel que não é o jarvis, chama `barrar` com
  "o hook não modela"; o filtro de `barrar` só mantém a recusa quando `controle_no_texto` casa, então a linha sem pedido
  ou brief da pasta de controle segue livre (N7 a N11 abaixo). Legível, comentário com a origem de cada guarda.
- Leitura por texto, fecha na dúvida, declarada em `docs/hooks.md:56` com o contorno (`git commit -F`).

## Sondas de caso legítimo (hook do 7a739fca contra o do 0f4facab, mesma fixture montada)
Roteiro `~/.forge-contrib/wt/tl-e6314/sondas.py` (o da E63.10 mais 14 linhas N1 a N14), saída em
`~/.forge-contrib/wt/tl-e6314/sondas.txt`; árvore velha por `git archive 0f4facab`.
- **As 44 linhas da E63.10 (S, R1 a R18, O, G, E, C): todas iguais**; nenhuma rotina dos subagentes passou a recusar.
- Iguais nas linhas novas: `echo $HOME` junto da leitura do pedido em `wt/` (N1), `git commit -m 'fix: HOME trocado'` e
  push (N7), `pip install -r` (N8), `ln -s a b` em `wt/` (N9), `mv …; source venv/bin/activate` sem controle (N10),
  `git archive … | tar -x -C ~/.forge-contrib/wt/…` (N11), `cat docs/briefs/b1.md; echo ok` na pasta de controle (N13).
- Passaram a recusar (rc 0 → 2), todas com pedido da pasta de controle e palavra da lista na mesma linha, como declarado:
  N5 (`mv $TMPDIR/a $TMPDIR/b && sed … docs/pedidos/v1.md`), N6 (`. venv/bin/activate && sed …`), N14
  (`HOME=$TMPDIR/f git status && sed …`), e N4 (`cd ~/.forge-contrib/wt/x && grep -n 'link' docs/pedidos/v1.md`), em
  que `link` é só o padrão do grep (ver A1).

## Ferramentas (citadas, não refeitas)
- Testes do domínio, por nome, no head 7a739fca, `TMPDIR=/tmp/claude-0` (fora de `~/.forge-contrib`):
  `HookSessaoDoForge.test_travas_do_conformidade`, `Hooks.test_fixtures_da_substituicao_no_projeto`,
  `Hooks.test_fixtures_do_controle_so_jarvis`, `Hooks.test_fixtures_da_escrita_no_indice` → `Ran 4 tests in 21.589s OK`.
- `bin/forge-mutante --processos 1 --ids W1,W5 tests/mutantes/v0479-conformidade-trilha-13.json` →
  `W1 · morreu · hooks/conformidade.py:3838`, `W5 · morreu · hooks/conformidade.py:3886`.
- Suíte inteira: sem PR nem run de CI na branch; não rerrodada aqui.

## Sondas
- S1 · tech-lead, cwd do projeto: `cd ~/.forge-contrib/wt/x && sed -n 1,5p docs/pedidos/v1.md > $TMPDIR/e.txt` · espera: rc 0 · obtido: rc 0 (0f4facab: rc 0)
- S2 · tech-lead, cwd do projeto: `cd ~/.forge-contrib/wt/x && HOME=$TMPDIR/f git status && sed -n 1p docs/pedidos/v1.md` · espera: rc 2 (A16) · obtido: rc 2 (0f4facab: rc 0)
- S3 · tech-lead, cwd do projeto: `cd ~/.forge-contrib/wt/x && grep -n 'link' docs/pedidos/v1.md` · espera: rc 0 (leitura) · obtido: rc 2 (0f4facab: rc 0)

## Achados
- A1 (recomendado) hooks/conformidade.py:3823 · `link`, `install`, `rename`, `mv` e `HOME` casam em qualquer posição, também como argumento entre aspas (`grep -n 'link' docs/pedidos/v1.md` em `wt/` recusa, S3); restringir as palavras de programa à posição de comando reduz o falso positivo sem abrir o A17.

## Parecer
Aprovado no head 7a739fca. O A16 e o A17 da segurança fecham pela lista de palavras que trocam o caminho na linha, com a
exceção da cópia de `wt/` desligada e a recusa limitada, pelo filtro de `barrar`, às linhas que citam o pedido ou o brief
da pasta de controle. Nas 44 linhas de rotina da E63.10 nenhuma passou a recusar; as novas recusas são as declaradas
("fecha na dúvida"), com contorno documentado. O falso positivo do padrão do grep (A1) é recomendado, não bloqueia.
