---
tipo: revisao-seguranca
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: 8c243582ee0eadd602956a67e210337560f33912
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: conf-base-dono

Pedido CONF-BASE-DONO (pareceres em CONF-BASE-DONO-REV, E2.1). Diff revisado: `origin/develop...8c24358` (base `daf2ffa`), 7 arquivos. Revisão estática, com sondas locais num repositório temporário (`HOME` próprio em `$TMPDIR`) que rodam o `bin/forge-check` da branch. `tests.test_conferencia_base_dono`: 14 testes, OK.

## Gatilhos
- `controles do Forge`: `bin/forge-check` (`forge-check entrega`, a conferência `R-PROVA`), `agents/conferente.md`, `agents/jarvis.md`.

## Achados
- A1 (bloqueante) bin/forge-check:835 · diferem_dos_dois_pais confere só o head: um merge maligno anterior (arquivo novo do autor posto no commit de integração) seguido de outra integração da base some do escopo (sonda: X.txt fora, "sem commit", rc 0)
- A2 (recomendado) bin/forge-check:638 · BASE_DO_DONO aceita a frase em qualquer ponto da linha (sonda: "proposta recusada: base do delta fixada pelo dono <sha> não vale" vira base) e não exige a DECISÃO DO DONO correspondente no pedido
- A3 (recomendado) bin/forge-check:748 · base do dono igual ao head é aceita e zera o delta (review, seguranca, qa: "sem commit (nada a conferir)", rc 0); a base do dono deveria ser ancestral próprio do head
- A4 (recomendado) bin/forge-check:4530 · --raiz-pedidos aceita qualquer pasta (outro projeto, $TMPDIR) e passa na frente de ~/.forge-contrib; docs/pedidos/ ali não é protegido pelo hook, então o Histórico que abre o --desde pode ser escrito por qualquer agente

## Detalhe dos achados
**Perguntas do brief, respondidas uma a uma.**

1. *Um agente que não é o Jarvis consegue gravar a linha "base do delta fixada pelo dono" e encurtar a conferência?* Não pelo caminho normal. A proteção não é por conteúdo (nenhum hook procura a palavra `conferida`): é por caminho, o arquivo inteiro do pedido, `hooks/conformidade.json:48` (`docs/pedidos/`) e `:49` (`~/.forge-contrib/docs/pedidos/`), só `jarvis`. A linha nova mora no mesmo arquivo e herda a mesma barreira; além disso, `pedido_na_entrega` (`bin/forge-check:752`) reprova o `--desde` quando a entrega comitou em `docs/pedidos/`, e o teste `test_a_base_do_dono_nao_vale_gravada_na_propria_entrega` cobre isso. Não estender o hook **não é bloqueante**. A brecha que sobra é a fonte do pedido fora das pastas protegidas (A4), anterior a esta mudança no argumento `<pedido>` como caminho e agora também por `--raiz-pedidos`.
2. *A base do dono pode estar fora da branch ou depois da entrega?* Fora da branch, não: `desde_valido` exige sha40 existente, ancestral do head e não ancestral do Base-sha (o teste "sha fora da branch" cobre). Depois da entrega, não. Igual ao head, sim (A3).
3. *O escopo de integração pode esconder arquivo novo de autor num merge?* Sim, com dois merges (A1). Com um merge só, o arquivo aparece (sonda A2: `confira "X.txt"`).
4. *O `--raiz-pedidos` lê pedido de outro projeto ou fora de `docs/pedidos/`?* Fora de `docs/pedidos/`, não: `dentro_da_raiz` (`bin/forge-check:926`) usa `realpath`; nas sondas, o symlink de `docs/pedidos/p1.md` para fora e a travessia `../../alvo/p1` saem com rc 2. De outro projeto (ou de qualquer pasta), sim (A4).

**A1 · bloqueante · média.** Evidência: `bin/forge-check:835-851`, chamada em `:888`. A função olha só os pais do head e pede que os commits do intervalo sem merge (`git log --no-merges`) estejam vazios. Assim, um merge *intermediário* pode trazer conteúdo próprio sem ser examinado. Caminho de ataque: o agente que implementa (sem má-fé basta: um arquivo esquecido numa resolução de conflito) faz `git merge --no-commit develop`, acrescenta `X.txt` e comita (M1). Depois a `develop` anda e ele integra de novo (M2). Com `--desde <conferida>` e head M2, `X.txt` não difere de M1 (o primeiro pai), sai da interseção e a saída é `escopo: integração da base (o que difere dos dois pais)` / `escopo: sem commit (nada a conferir)`, rc 0, nas etapas `review`, `seguranca` e `qa`. O código entra sem passar pela conferência `R-PROVA` do delta, que é o controle que a mudança relaxa. Correção mínima: só tratar como integração quando o único commit próprio do intervalo (`git rev-list <de>..<head> --not origin/<Base>`) for o próprio head, um pai for `<de>` (ou o contiver) e o outro for ancestral de `origin/<Base>`. Fora disso, `None` (a conferência de hoje). Mais um teste com os dois merges. Esforço P. Dono: `tech-lead`.

**A2 · recomendado · baixa.** Evidência: `bin/forge-check:638` (`^\s*-\s.*\bbase do delta…`). Mesma folga que a `CONFERIDA` já tinha em `:637`. Quem escreve é só o Jarvis, então não há atacante externo: o risco é uma linha que cita a frase (recusa, proposta) virar base. Correção mínima: ancorar a forma (`- <data hora>: base do delta fixada pelo dono <sha40>`) e exigir, no `## Decisões do usuário (registro literal)`, uma `DECISÃO DO DONO` que cite o mesmo sha40. É o que o próprio pedido põe fora do escopo: "aceitar base sem decisão do dono registrada". Esforço P. Dono: `tech-lead`.

**A3 · recomendado · baixa.** Evidência: `bin/forge-check:743-749` (`e_ancestral(c, head)` vale para `c == head`). Para a `conferida` isso é certo (nada novo desde a conferência). Para a base do dono, significa que nada da entrega foi conferido, sem nenhum aviso. Correção mínima: na origem `dono`, exigir `c != head`. Esforço P. Dono: `tech-lead`.

**A4 · recomendado · média.** Evidência: `bin/forge-check:4530` (qualquer pasta, posta na frente de `RAIZES_DE_BRIEF`) e `hooks/conformidade.py:569-590` (o `docs/pedidos/` com dono só é casado relativo à raiz da sessão ou como `~/.forge-contrib/docs/pedidos/`). Sonda: `--raiz-pedidos outro` lê `outro/docs/pedidos/p1.md` (`origem:` impresso) e aceita a base do dono escrita ali. Caminho de ataque: um agente grava um pedido com a linha da base numa pasta que o hook não guarda, e o conferente é chamado com essa pasta. Não é bloqueante por proporcionalidade: a pasta vem da mensagem do Jarvis, que o autor não escreve, e o argumento `<pedido>` como caminho de arquivo (`bin/forge-check:701`, anterior a esta branch) já tinha a mesma exposição. Correção mínima: aceitar `--raiz-pedidos` só em raiz guardada pelo hook (`~/.forge-contrib` ou a cópia principal) ou reprovar o `--desde` quando o pedido veio de fora delas. Em `agents/conferente.md:81`, dizer que o `<dir>` vem da mensagem do Jarvis. Esforço P. Dono: `tech-lead`.

## Plano em cartões
- A1: corrigir antes do PR (volta à branch, `tech-lead`), com o teste dos dois merges.
- A2, A3, A4: podem entrar na mesma volta (esforço P cada) ou virar cartão.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais com o `forge-check` da branch, `python3 -m unittest tests.test_conferencia_base_dono`. Lacunas: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH. A entrega não toca workflow, dependência nem configuração com segredo, e o CI do Forge roda as suas varreduras.
