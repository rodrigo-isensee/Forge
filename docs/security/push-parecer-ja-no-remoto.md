---
tipo: revisao-seguranca
contrato: 1
pedido: versao-035
branch: melhoria/push-parecer-ja-no-remoto
commit: d2460c939f3aaab22345a5f97675051e1bc7a7e6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-06
---
# Review de segurança: versao-035 (E3, PUSH-PARECER-JA-NO-REMOTO)

## Gatilhos
Hook de push (`R-VERIFY`, `R-MAIN`), controle do Forge que afrouxa "nada novo chega ao remoto sem suíte" (decisão do dono de 2026-11-05 15:20, rótulo `afrouxa-regra`) e uma chamada de rede nova (`git ls-remote`).

## Achados
- A1 (recomendado) .githooks/pre-push:197 · o ls-remote em $2 aplica url.insteadOf e o push aplica pushInsteadOf: com as regras encadeadas (config ou -c) o hook consulta outro repositório e pula a suíte (reproduzido no git 2.43). Falhar fechado se `git ls-remote --get-url -- "$2"` diferir de $2

## Detalhe dos achados
**A1.** Evidência: `.githooks/pre-push:197` consulta `git ls-remote -- "$destino"` com `destino="$2"` (`:189`, `:207`, `:296`). O git entrega em `$2` a URL de envio já reescrita por `url.<y>.pushInsteadOf`; o `ls-remote` sobre essa URL ainda aplica `url.<z>.insteadOf`. Reprodução no scratchpad: `git -c url.Z.insteadOf=Y -c url.Y.pushInsteadOf=orig push orig HEAD:refs/heads/melhoria/x`, com `Z.git` contendo o commit e `Y.git` vazio; o hook recebeu `2=Y.git`, `ls-remote --get-url -- Y.git` devolveu `Z.git` e o `ls-remote` achou `melhoria/x` no sha local. No hook real isso daria o pulo e o commit chegaria a `Y.git` sem suíte. Caminho de ataque: só quem escreve a configuração do repositório ou a linha de comando do `git push` (agente com instrução injetada). Severidade: baixa. Esse mesmo ator já desliga o hook inteiro com `git -c core.hooksPath=/dev/null push`, então o pulo não lhe dá capacidade nova, e o CI do PR roda a suíte inteira; por isso fica recomendação, não bloqueante (`R-REVIEW`). É o A3 do review (`docs/reviews/push-parecer-ja-no-remoto.md`), agora com a divergência provada. Correção mínima (uma linha, antes do laço de `ja_no_remoto`): `[ "$(git ls-remote --get-url -- "$destino" 2>/dev/null)" = "$destino" ] || return 1`, mais um caso na tabela do teste com as duas regras encadeadas, em que a suíte precisa rodar. Alternativa: registrar como residual no corpo do PR, junto do A10 do modelo de ameaças, como o Histórico do pedido já prevê (decisão técnica de 12:35). Esforço: P. Dono: `forge:tech-lead` (autor do E3).

**Controles do modelo de ameaças (`docs/security/ameacas/versao-035.md`, E3), conferidos no head d2460c9:**
- C-1 falha fechada: `GIT_TERMINAL_PROMPT=0 timeout 20` (`:197`); rc diferente de 0, saída vazia, sha inválido ou objeto ausente devolvem 1 (`:197`, `:199`, `:201`). O `timeout` sem `--foreground` mata o grupo de processos, então um `ssh` filho não segura o pipe da substituição de comando.
- C-2: o desenho e o C-2 pediam `$1`; o review provou (seu A1) que `$1` lê a `url` de busca enquanto o push vai à `pushurl`. O código usa `$2` (`:207`, `:296`), com recusa de vazio e de `-*` (`:192`), `--` e aspas, sem `eval`. A intenção do C-2 ("o destino escolhido pelo git, nunca o ambiente") passa a ser cumprida por `$2`; o texto do C-2 e do T-3 no modelo de ameaças (fora desta branch) fica para revisão na próxima delegação do modelo. Conferi também URL relativa chamada de subpasta: o git resolve a do push a partir da raiz da worktree, a mesma pasta em que o hook roda (`:180`), então as duas leituras coincidem.
- C-3, T-2: a ref volta comparada pelo nome inteiro, linha a linha (`:198`); só `refs/heads/?*`, sem main, homolog, develop nem caractere de controle (`:195`). O teste cobre o casamento pela cauda com `refs/heads/a/refs/heads/melhoria/z`, linha que o `ls-remote` devolve de fato.
- C-4, T-7: tudo ou nada, `n_envios -gt 0` e `n_envios -eq n_refs` (`:190`) e o vetor do mesmo tamanho (`:191`); tag, remoção misturada ou ref nova devolvem 1.
- C-5, T-5, T-6: as duas chamadas vêm depois do laço das recusas (`:133-160`), do stdin vazio e do PREPUSH-DELETE (`:164-175`), fora do `--suite` (`:190`, `:207`); o `--status` sai antes (`:127`). O laço só ganhou a linha `:135`, que não muda nenhuma recusa.
- C-6: igualdade ou `cat-file -e "${achado}^{commit}"` seguido de `merge-base --is-ancestor` (`:200-201`); sha de 40 ou 64 hexadecimais nos dois lados (`:187`, `:196`, `:199`). Nenhum `fetch`, ref de rastreio ou `FETCH_HEAD`. O caso "local ancestral do remoto" não reescreve nada: o push que se segue ao `exit 0` é recusado pelo próprio git (o sha antigo que ele manda não confere com o remoto).
- C-7: a segunda consulta vem depois de `fila_sair` (`:294-296`) e antes de `: > /proc/self/fd/9`; a trava solta com o `exit`. Ela segura a trava por até 20 s por ref, dentro do orçamento do modelo.
- C-8, T-1: o caminho do pulo não escreve `.verde`, `.dirigida` nem outro estado; `verde` e `dirigida` só são definidos depois (`:226`).
- C-9: mensagem fixa em stderr com ref e sha7 (`:205`); a ref com controle já saiu por `:195`.
- C-10: nenhuma variável `FORGE_*` liga ou desliga o pulo; a lista de recusas não ganhou exceção.
- C-11: o fragmento `changelog.d/push-parecer-ja-no-remoto.md` cita o afrouxamento; o rótulo `afrouxa-regra` e a medida de reversão vão no PR (E2.7, E2.8).
- T-8: nenhuma mensagem nem doc sugere `--no-verify` ou `--force`.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum novo neste parecer. O A10 do modelo (o remoto recebeu o mesmo commit de quem não passou pelo hook) segue como residual aceito pelo desenho, coberto pelo CI do PR, a registrar no corpo do PR com `afrouxa-regra`; o A1 acima entra junto se não for corrigido.

Ferramentas: `python3 -m unittest tests.test_pre_push_ja_no_remoto` no head d2460c9: 2 testes (22 casos em subTest), OK (24,6 s). A suíte inteira não rodei (D-5): o push de d2460c9 a rodou (Histórico do pedido, 14:39). Reproduções em git 2.43.0 no scratchpad. Faltam no ambiente, registradas como lacuna: `shellcheck`, `gitleaks`, `zizmor`, `actionlint`, `semgrep` (nenhuma no PATH; o diff não toca workflow nem segredo).

## Parecer
Aprovado. Lido: o E3 do escopo, as decisões do dono e o Histórico em `docs/pedidos/versao-035.md`, a seção E3 de `docs/arquitetura/versao-035-desenho.md`, o E3 do modelo de ameaças com a revisão pós-implementação, o parecer de review de 72bf750 e o diff `origin/develop...d2460c9` (8 commits: `.githooks/pre-push`, `tests/test_pre_push_ja_no_remoto.py`, `docs/hooks.md`, `changelog.d/`). O afrouxamento fica na leitura estreita que o dono autorizou: só pula quando o destino real do push já tem cada branch enviada no mesmo sha ou num descendente, depois de todas as recusas, sem gravar prova. C-1 a C-11 cumpridos, com o C-2 cumprido por `$2`, que é a correção do A1 do review. O único achado (A1) é recomendação de endurecimento barata; não devolve.
