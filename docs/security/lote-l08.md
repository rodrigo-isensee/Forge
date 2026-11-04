---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: 874c89ec82a86840262c5c4a5b93eba48554eb5c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (lote L08)

Diff revisado: `4f53bde..874c89e` (E10, E12, E16, E7, E19), em leitura estática; rodei só os testes dos arquivos tocados (D-5).

## Gatilhos
Controles do Forge (R-SEGURANCA): `bin/forge-check` (`pr`, `entrega`, `brief`), `docs/regras/R-PROVA.md` e a conferência de entrega (`agents/conferente.md`, `agents/jarvis.md`).

## Achados
- A1 (recomendado) bin/forge-check:907 · O E7 aceita qualquer linha do Histórico com `conferida <sha40>`, não só `entrega conferida`; o Histórico real já tem linhas `conferida <sha>` com veredito `não cumpriu`. Exija `entrega conferida <sha40>` no `pr`.
- A2 (recomendado) bin/forge-check:717 · O E7 falha aberto: sem pedido achado ou sem `## Histórico` (linha 719), o `pr` da linha de comando aprova sem a conferência do head; na linha de comando do Jarvis, prefira a recusa com o motivo.
- A3 (recomendado) bin/forge-check:818 · `gh pr view <n>` sem `--repo` usa o repositório padrão do gh; com mais de um remoto (fork e origem), o #n pode ser de outro repositório. Passe `--repo` do origin ou imprima a URL do PR.

## Detalhe dos achados
**Respostas ao foco.**
- E10: o head não é forjável por quem não controla o `gh` do PATH (fora do modelo). A resposta só vale com `state == MERGED`, `headRefOid` em sha40 exato (`SHA40.fullmatch`, sem sha curto, então sem ambiguidade) e presente no clone (`rev-parse --verify <sha>^{commit}` igual a ele), e com `headRefName` sem caractere de controle; `--pr` e `--ref` juntos dão rc 2. PR de fork: o `headRefName` escolhido por quem abriu o fork só escolhe *qual* parecer, que ainda precisa casar com o head pelo `commit_vale`. Por isso o fork não ganha nada. O único vetor que sobra é o A3.
- E12: o resultado não confere menos. A base do dono igual ao head já era recusada pelo `desde_valido`. Agora a proposta cai no Base-sha, que é a branch inteira, mais escopo. A conferida de outra branch deixa de abrir o Base-sha quando há conferida da própria branch, e a conferida já contida na base passa a abrir o Base-sha. Nos dois casos o intervalo é o certo ou um intervalo maior. As duas expectativas antigas mudaram nessa direção (`tests/test_conferencia_base_dono.py`, `tests/test_mensagem_conferente.py`).
- E16: só acrescenta texto à recusa que o `commit_vale` já dava (`commit_junto_do_parecer` não decide nada). Não muda a superfície de ataque.
- E7: um agente fora do Jarvis não forja a linha. `docs/pedidos/` (no clone e em `~/.forge-contrib`) é só do jarvis em `hooks/conformidade.json:48-50`, e `caminho_do_pedido` lê a cópia principal antes da worktree. Também não troca o pedido pelos briefs, porque `docs/briefs/` é só do jarvis (`hooks/conformidade.json:51-53`) e o `pr` recusa dois pedidos para a mesma branch. A conferida precisa ser sha40 existente, ancestral do head e com só LIVRES e o fragmento do changelog depois dela. A falha que sobra é de redação do próprio Jarvis (A1) e de falha aberta (A2).
  - A1: caminho realista. O Jarvis registra uma rodada reprovada como "E1.2 conferida <sha> ... não cumpriu", forma que já aparece em pedidos antigos de `~/.forge-contrib/docs/pedidos/`. Com isso, o `pr` libera o QA e o merge sobre um head que o conferente reprovou. Severidade baixa (quem escreve é confiável e o erro é dele). Correção mínima: no `conferencia_do_head`, uma expressão própria `^\s*-\s.*\bentrega conferida ([0-9a-f]{40})\b`, e manter o `CONFERIDA` atual no `--desde`. Esforço P. Dono: tech-lead.
  - A2: o pedido sem Histórico só gera aviso no stderr. Quem pode tirar o Histórico é só o Jarvis, e o caso sem pedido é o CI, de propósito. Severidade baixa. Correção mínima: com o pedido achado e sem `## Histórico`, devolver a violação em vez do aviso. Esforço P. Dono: tech-lead.
- E19: o executor não marca o tipo. `Tipo: ato-github` vem do brief do Jarvis (hook em `docs/briefs/`), e a etapa exige `--branch —`, um único `--brief` com o mesmo pedido, Base e Base-sha, e nenhuma PQ `sha` ou `push`. Mesmo um brief de código marcado assim por engano não chega ao merge: o `pr` do E7 ainda cobra `entrega conferida <sha40>` do head, e o ato-github não produz essa linha (com a ressalva do A2).
- A3: severidade baixa. Exige um clone com dois remotos e um PR #n mesclado também no outro repositório, com head presente no clone e pareceres válidos para ele. A saída imprime o `headRefName`, o que ajuda a perceber a troca. Correção mínima: `--repo` derivado de `git remote get-url origin`, ou imprimir o `url` do PR. Esforço P. Dono: tech-lead.

Nada disso bloqueia: nenhum caminho dá a um agente sem escrita em `docs/pedidos/` ou `docs/briefs/` um jeito de pular a conferência.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados (só os arquivos tocados, D-5): `python3 -m unittest tests.test_forge.PrMescladoPeloHead tests.test_forge.TesteEParecerSeparados tests.test_forge.ConferenciaPresaAoHead tests.test_forge.EntregaAtoGithub tests.test_conferencia_base_dono tests.test_mensagem_conferente tests.test_volta_por_delta tests.test_erros_no_brief`, com `Ran 173 tests ... OK`. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor, actionlint. O diff não toca workflow nem dependência.
