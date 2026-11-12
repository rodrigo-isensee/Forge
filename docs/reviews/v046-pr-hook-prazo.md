---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/pr-hook-prazo
commit: 4ae51318d06223e29c3d09913965dd081d4ddb62
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.3, melhoria/pr-hook-prazo, PR-HOOK-PRAZO)

Escopo lido: `git diff origin/develop...4ae51318` (base d3453407): `bin/forge-check` (+70), `bin/forge-testes` (mapa), `hooks/_comum.py`, `hooks/parecer.py`, `tests/test_pr_hook_prazo.py`, `tests/test_hooks.py`, `tests/apoio_volta_unica.py`, `tests/test_testes_tocados.py`, 12 fixtures de `tests/hooks/parecer/`, `tests/mutantes/v046-pr-hook-prazo*.json` (M1-M33, 2 isentas) e `changelog.d/pr-hook-prazo.md`. Instância que não fez a entrega. Classe C.

## Achados
- A1 (recomendado) hooks/parecer.py:1007 · o contorno "rode antes forge-check pr" vale para todo prazo vencido do hook (gh pr ready, gh pr merge, git merge/pull, texto longo), mas só o gh pr create fora do rascunho lê o resultado gravado; nos outros casos não destrava; escolher o contorno pela linha e manter CONTORNO_DO_TETO no resto
- A2 (recomendado) hooks/parecer.py:586 · nos projetos o gh pr create --draft também passa por verificar com gravado=True: todo PR de projeto passa a pedir o forge-check pr antes, com a conferência de entrega (R-PROVA); o fragmento diz "abertura de PR sem rascunho"; dizer o efeito nos projetos no fragmento e no corpo do PR
- A3 (recomendado) bin/forge-check:1541 · uma pasta por head em <git-common-dir>/forge/pr/ sem limpeza: cresce a cada head conferido; podar os heads que deixaram de ser ponta de branch (no forge-fechar ou ao gravar) num item próprio
- A4 (recomendado) bin/forge-check:1520 · 374 linhas de código e teste (M14): 111 de produção (forge-check 70, forge-testes 4, hooks 37) e 263 de teste, 239 no módulo próprio; um comportamento só; o corpo do PR leva `teto: excedido, 374 linhas, <motivo>`

## Sondas

## Parecer
**Aprovado.** Faz o que a E20 pede: o `forge-check pr` da linha de comando (fora do `--previo` e do `--pr`) grava aprovado ou reprovado por head em `<git-common-dir>/forge/pr/<head>/`, com branch, `base_sha` resolvida pela mesma `base_do_delta` do hook (K-164) e os pedidos da branch; o hook só libera o `gh pr create` com o aprovado de todos os pedidos da branch no mesmo head, branch e base, recusa com a violação gravada no reprovado e, sem registro, recusa mesmo sem violação e diz o comando. Registro ilegível, malformado, de outra branch, de outro head ou de outra base vira ausente (falha fechada). `gh pr ready`, `gh pr merge` e `git merge` seguem com a conferência de sempre (teste com a checagem trocada por saída 97). O fragmento traz medida e volta atrás (`gravado=False`, uma linha); o afrouxamento é decisão do dono (diretriz 3, item E20).

Conferências pedidas no brief:
- **Merge 1a8a97ec:** a resolução de `bin/forge-testes` soma `test_pr_hook_prazo` às duas listas da develop sem perder entrada; a contagem do `test_testes_tocados` 78→79 bate (o módulo passou).
- **Isentas (v046-pr-hook-prazo-5.json):** as duas valem. `base_sha or ''` só compõe o nome do arquivo; a leitura percorre a pasta e casa pelo conteúdo, então o mutante é equivalente. `'veja a saída dele'` é texto de reserva do motivo; o veredito (recusa) não muda.
- **Mutantes:** uma linha de guarda mudada, um mutante (M1-M33), cada um com teste de comportamento do ramo de falha; a cobertura rc=0 e 33/33 mortos são do autor (E20.2), não refeitos aqui. O teste que roda o `forge-check` limpa o ambiente e usa `-I` (AR-4).
- **Falhas locais do autor:** os fixtures `agentes/*` e `pesado/mesma-sessao-libera` rodados só eles, um lote de cada vez: 5 falhas na branch e as mesmas 5 na `origin/develop` (8b5a44d5, exportada por `git archive`), todas de PID/sessão de outro namespace (`"sessao": "s1"` e `"pidns"` ausentes). Não vêm desta entrega; o CI decide.
- **Teto:** o PR deve citar o teto (A4).

Segurança: o parecer `docs/security/v046-pr-hook-prazo.md` (E20.4) aprovou com A1 (registro sem o sha256 do forge-check que gravou) e A2 (`hooks/conformidade.py:951`, já existia, cartão E20.6); citados, não refeitos.

Testes rodados no head (um módulo por vez): `tests.test_pr_hook_prazo` 15 OK; `tests.test_testes_tocados` 149 OK; `tests.test_hooks_volta_lancador` 22 OK; fixtures do `test_hooks` do hook `parecer` 454 OK (os de prazo de produção ficam no CI). A suíte inteira fica no CI do PR.

A conferência de entrega deu rc=1 por base antiga (237 commits), defeito da ferramenta em correção na E23.17; não é achado desta entrega.
