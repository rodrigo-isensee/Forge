---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/pr-hook-prazo
commit: e8c4cd55cb291e562c454b1cb15f16f4b3a875cf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.3, melhoria/pr-hook-prazo, PR-HOOK-PRAZO)

## Revalidação por delta (E23.92, head e8c4cd55, merge da develop a986c292)
Delta lido: `forge-check parecer delta docs/reviews/v046-pr-hook-prazo.md`, intervalo cf1cc45d..e8c4cd55, sem o que veio da base; no domínio só `bin/forge-testes` e `tests/test_testes_tocados.py` (resolução do conflito do mapa). Instância que não fez a entrega, sem reler o resto.
- **Resolução do merge:** contra a develop (`git diff e8c4cd55^2 e8c4cd55`) a branch soma só `test_pr_hook_prazo` às duas listas (FORGE_CHECK e a do `hooks/`) e mantém o `test_hook_git_comum` vindo da develop; a contagem do `test_testes_tocados` vai 79→80 e o comentário cita as duas entradas. Nenhuma entrada da develop se perdeu; nenhum código de produção mudou.
- **`.claude/CLAUDE.md`:** a mudança (ENVIO-LEVE) veio inteira da develop; o head é igual à develop nesse arquivo. Fora do domínio desta entrega.
- **Teste rodado no head (R-TETO, só o afetado):** `python3 -m unittest tests.test_testes_tocados` 149 OK, 1 pulado (46 s). A suíte inteira fica no CI do PR.
- Sem achado novo; A4 segue (o PR cita o teto).

## Revalidação por delta (E20.26, head cf1cc45d, volta E20.25)
Delta lido: `forge-check parecer delta docs/reviews/v046-pr-hook-prazo.md`, intervalo c6577dbb..cf1cc45d, no domínio só `tests/mutantes/v046-pr-hook-prazo-7.json` (+36) e `tests/test_pr_hook_prazo.py` (+23); nenhum código de produção. Instância que não fez a entrega, sem reler o resto.
- **Teste novo** `test_poda_nao_segue_link_nem_abre_arquivo_nem_apaga_a_gravada` (tests/test_pr_hook_prazo.py:309): com `for-each-ref` vazio (o head fora das pontas), o link com nome de sha para uma pasta de fora não é seguido (`alvo.json` fica), o arquivo com nome de sha não é aberto como pasta (sem o aviso) e a pasta recém-gravada fica. Roda em processo, sem subprocesso (AR-4 não se aplica); asserções de comportamento, não do texto da fonte.
- **Mutantes M42-M44** (bin/forge-check:1544, guardas já existentes, A2 e A3 do QA): cada `de` casa uma vez só na fonte; pela leitura, M42 faz o `iterdir` seguir o link e apagar `alvo.json`, M43 abre o arquivo e cai no aviso, M44 apaga a pasta gravada; os três morrem por asserção, independentemente da ordem do `iterdir`. Mortos e cobertura rc 0 são do autor (E20.25), não refeitos aqui.
- **Tamanho:** 484 linhas de código e teste (`git diff --numstat --no-renames d3453407...cf1cc45d`, a spec de mutantes fora); A4 atualizado.
- **Teste rodado no head (R-TETO, só ele):** `python3 -m unittest tests.test_pr_hook_prazo` 18 OK (44 s). A suíte inteira fica no CI do PR.
- Sem achado novo.

## Revalidação por delta (E20.21, head c6577dbb, volta E20.11)
Delta lido: `forge-check parecer delta docs/reviews/v046-pr-hook-prazo.md`, intervalo 4ae51318..c6577dbb, no domínio: `bin/forge-check`, `changelog.d/pr-hook-prazo.md`, `hooks/_comum.py`, `hooks/parecer.py`, `tests/apoio_volta_unica.py`, `tests/mutantes/v046-pr-hook-prazo{,-4,-6}.json`, `tests/test_pr_hook_prazo.py`. Instância que não fez a entrega, sem reler o resto.
- **A1 resolvido:** o "Corrigir" do prazo vencido sai do `executar` e vira `hook.contorno_do_prazo`, posto só em `verificar` com `motivo` (o `gh pr create` sem resultado gravado, hooks/parecer.py:563); o resto usa `CONTORNO_DO_TETO` (hooks/_comum.py:2785). O teste roda o hook de produção com o `cmd_pr` lento: no `gh pr create` diz "rode antes forge-check pr", no `git merge` não.
- **A2 resolvido:** o fragmento diz o efeito nos projetos (também o `--draft`, com a conferência de entrega).
- **A3 resolvido:** `podar_resultados` (bin/forge-check:1535) apaga, depois de gravar, as pastas de head de 40 hex que não são ponta de `refs/heads` nem `refs/remotes`, sem seguir link; sem a lista das pontas não apaga nada, e a falha só avisa (motivo curto, sem caminho). Testado: órfã apagada; ponta, gravada e pasta alheia ficam; `for-each-ref` falho não apaga; subpasta faz avisar.
- **A1 da segurança:** o registro leva `escritor` (sha256 do `forge-check` que gravou) e a leitura descarta o de outro escritor ou sem ele (bin/forge-check:1593); o hook carrega o `forge-check` do plugin (`_comum.forge_check`), então só o gravado por ele libera. Subtestes "outro escritor" e "sem escritor" recusam. O mérito da proteção fica com a segurança (E20.22).
- **A1 do QA:** `um_registro` conta antes de desempacotar e a leitura da violação passa por `str()`: na base sem gravação o teste falha por asserção, não por erro (M25 morre por asserção).
- **Mutantes:** M7 e M25 acompanharam a linha mudada (AR-12 em dia); M34-M41 novos, um por linha de guarda mudada (poda: `if cod`, a condição, o `except`, o `return` antes da poda, o aviso; leitura: `escritor`; hook: `if motivo`, o `or`), cada um com teste de comportamento do ramo de falha. 41/41 mortos e a cobertura são do autor (E20.11), não refeitos aqui.
- **Tamanho:** 461 linhas de código e teste (`git diff --numstat --no-renames d3453407...c6577dbb`: forge-check 97, forge-testes 4, _comum 6, parecer 22, test_hooks 19, test_pr_hook_prazo 311, test_testes_tocados 2); um comportamento só. Segue A4 com o número novo. Vai para a versão seguinte.
- **Teste rodado no head (R-TETO, só ele):** `python3 -m unittest tests.test_pr_hook_prazo` 17 OK (38 s). A suíte inteira fica no CI do PR.

Escopo lido: `git diff origin/develop...4ae51318` (base d3453407): `bin/forge-check` (+70), `bin/forge-testes` (mapa), `hooks/_comum.py`, `hooks/parecer.py`, `tests/test_pr_hook_prazo.py`, `tests/test_hooks.py`, `tests/apoio_volta_unica.py`, `tests/test_testes_tocados.py`, 12 fixtures de `tests/hooks/parecer/`, `tests/mutantes/v046-pr-hook-prazo*.json` (M1-M33, 2 isentas) e `changelog.d/pr-hook-prazo.md`. Instância que não fez a entrega. Classe C.

## Achados
- A1 (recomendado) hooks/parecer.py:1007 · resolvido em c6577dbb (hooks/parecer.py:563): o contorno "rode antes forge-check pr" só no gh pr create sem resultado gravado; no resto, CONTORNO_DO_TETO
- A2 (recomendado) hooks/parecer.py:586 · resolvido em c6577dbb: o fragmento diz que nos projetos o gh pr create --draft também pede o forge-check pr antes, com a conferência de entrega (R-PROVA)
- A3 (recomendado) bin/forge-check:1541 · resolvido em c6577dbb (podar_resultados, bin/forge-check:1535). Era: uma pasta por head em <git-common-dir>/forge/pr/ sem limpeza: cresce a cada head conferido; podar os heads que deixaram de ser ponta de branch (no forge-fechar ou ao gravar) num item próprio
- A4 (recomendado) bin/forge-check:1529 · 484 linhas de código e teste (M14) no head cf1cc45d, 334 no módulo de teste próprio; um comportamento só; o corpo do PR leva `teto: excedido, 484 linhas, <motivo>`

## Sondas

## Parecer
**Aprovado no head e8c4cd55** (revalidação E23.92: só a resolução do mapa no merge da develop, sem achado novo; E20.26: só teste e spec, sem achado novo; E20.21: A1-A3 e os achados da segurança e do QA tratados; resta A4). Na E20.3, sobre 4ae51318: faz o que a E20 pede: o `forge-check pr` da linha de comando (fora do `--previo` e do `--pr`) grava aprovado ou reprovado por head em `<git-common-dir>/forge/pr/<head>/`, com branch, `base_sha` resolvida pela mesma `base_do_delta` do hook (K-164) e os pedidos da branch; o hook só libera o `gh pr create` com o aprovado de todos os pedidos da branch no mesmo head, branch e base, recusa com a violação gravada no reprovado e, sem registro, recusa mesmo sem violação e diz o comando. Registro ilegível, malformado, de outra branch, de outro head ou de outra base vira ausente (falha fechada). `gh pr ready`, `gh pr merge` e `git merge` seguem com a conferência de sempre (teste com a checagem trocada por saída 97). O fragmento traz medida e volta atrás (`gravado=False`, uma linha); o afrouxamento é decisão do dono (diretriz 3, item E20).

Conferências pedidas no brief:
- **Merge 1a8a97ec:** a resolução de `bin/forge-testes` soma `test_pr_hook_prazo` às duas listas da develop sem perder entrada; a contagem do `test_testes_tocados` 78→79 bate (o módulo passou).
- **Isentas (v046-pr-hook-prazo-5.json):** as duas valem. `base_sha or ''` só compõe o nome do arquivo; a leitura percorre a pasta e casa pelo conteúdo, então o mutante é equivalente. `'veja a saída dele'` é texto de reserva do motivo; o veredito (recusa) não muda.
- **Mutantes:** uma linha de guarda mudada, um mutante (M1-M33), cada um com teste de comportamento do ramo de falha; a cobertura rc=0 e 33/33 mortos são do autor (E20.2), não refeitos aqui. O teste que roda o `forge-check` limpa o ambiente e usa `-I` (AR-4).
- **Falhas locais do autor:** os fixtures `agentes/*` e `pesado/mesma-sessao-libera` rodados só eles, um lote de cada vez: 5 falhas na branch e as mesmas 5 na `origin/develop` (8b5a44d5, exportada por `git archive`), todas de PID/sessão de outro namespace (`"sessao": "s1"` e `"pidns"` ausentes). Não vêm desta entrega; o CI decide.
- **Teto:** o PR deve citar o teto (A4).

Segurança: o parecer `docs/security/v046-pr-hook-prazo.md` (E20.4) aprovou com A1 (registro sem o sha256 do forge-check que gravou) e A2 (`hooks/conformidade.py:951`, já existia, cartão E20.6); citados, não refeitos.

Testes rodados no head (um módulo por vez): `tests.test_pr_hook_prazo` 15 OK; `tests.test_testes_tocados` 149 OK; `tests.test_hooks_volta_lancador` 22 OK; fixtures do `test_hooks` do hook `parecer` 454 OK (os de prazo de produção ficam no CI). A suíte inteira fica no CI do PR.

A conferência de entrega deu rc=1 por base antiga (237 commits), defeito da ferramenta em correção na E23.17; não é achado desta entrega.
