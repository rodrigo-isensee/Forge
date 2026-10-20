---
tipo: revisao-seguranca
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: d6b9b352af4b1ee40f4d3d2e06b20909a3321546
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: rotulo-so-dono (revalidação do delta da volta 3)

Escopo: o delta da volta 3, `git diff 3b266e414f50a67b978725c7db6632fb1ba47ad1 d6b9b352af4b1ee40f4d3d2e06b20909a3321546` (a fixture `contrib-sessao-forge-raiz-pr-edit-rotulo-libera.json` e o teste novo em `tests/test_hooks.py`). Este parecer substitui o anterior (aprovado sobre 6ec5095). O `forge-check delta` sobre o parecer anterior lista também o que veio da `develop` pelo merge 3b266e4 (`hooks/agentes.py`, fixtures de `agentes`, R-TETO e R-WIP, release 0.23.0); conferido que não é deste PR: `git diff bd204b8 d6b9b35 -- hooks/agentes.py` vazio. Método: leitura estática, inventário das fixtures que citam o rótulo, `tests.test_hooks` com o PATH reduzido a `/usr/bin:/bin` (32 OK, 48 s; o `gh` real em `/usr/bin` sem credencial legível) e uma mutação numa cópia em `$TMPDIR` (fixture sem o `gh` falso: o teste novo falha). Sem rede e nenhum rótulo real.

## Gatilhos
`R-SEGURANCA`: fixture e teste do hook de controle (conformidade), que guarda o rótulo `afrouxa-regra`.

## Achados

## Detalhe dos achados

### Hook e invariantes: sem mudança
`git diff --stat 6ec5095 d6b9b35 -- hooks/conformidade.py` vazio; `tests/config.json` só difere de 6ec5095 pelo que veio da `develop`, e contra a `develop` (bd204b8) traz apenas as invariantes já revisadas deste PR. A guarda do rótulo é a mesma aprovada no parecer anterior.

### A fixture hermética não esconde caminho com outra conta
A fixture passa a pôr `bin/gh` (imprime o login do dono) à frente no PATH; o comando segue `gh pr edit 70 --remove-label afrouxa-regra`, espera 0. Antes ela dependia da credencial da máquina (só passava onde o `gh` real era do dono). O `gh` falso do dono aparece só nas 3 fixtures que esperam liberar (esta, `rotulo-so-dono-pr-edit-conta-do-dono-libera` e `rotulo-so-dono-api-labels-conta-do-dono-libera`); as que esperam barrar usam `outra-pessoa` ou `exit 1`, inclusive a remoção (`rotulo-so-dono-remover-rotulo-exige-dono`, conta ilegível barra). A `corpo-cita-rotulo-libera` libera com `outra-pessoa`, e está certo: o rótulo só aparece no corpo. Remover com outra conta segue barrado (sonda do parecer anterior; o hook não mudou). O `gh` falso existe só na pasta temporária da fixture; o hook lê a conta pelo PATH do próprio processo, não pelo de uma atribuição na linha do comando.

### O teste estrutural obriga o gh falso
`test_fixtures_da_sessao_do_forge_que_citam_o_rotulo_usam_o_gh_falso` (tests/test_hooks.py:383) cobre toda fixture com `forge: false` e o `plugin.json` na raiz cuja entrada cita `afrouxa-regra`: exige `bin/gh` nos arquivos, executável e o PATH começando por `{tmp}/proj/bin:`, com piso de 10 fixtures. Mutação conferida: tirar o `gh` falso desta fixture faz o teste falhar.

### Recomendações (não bloqueiam)
- **R9 (informativa) Filtro literal do teste novo.** Evidência: tests/test_hooks.py:391 só conta a fixture cuja entrada traz `afrouxa-regra` em minúsculas. Hoje duas fixtures da sessão do Forge ficam fora do filtro (`rotulo-so-dono-graphql-outra-conta-bloqueia`, mutação sem o nome, e `rotulo-so-dono-pr-edit-erro-na-conta-bloqueia`, `Afrouxa-Regra`), embora ambas já tragam o `gh` falso. Caminho: uma fixture futura nessas formas sem o `gh` falso dependeria da credencial da máquina; é risco de teste não hermético, não de contorno da guarda. Correção mínima: exigir o `gh` falso em toda fixture da sessão do Forge (sem o filtro do rótulo) ou comparar sem caixa e incluir `addLabelsToLabelable`/`labels`. Esforço: P. Dono: tech-lead (pode ir no cartão ROTULO-VARIAVEL).
- **R7, R8, R1, R6** e o registro do dono no corpo do PR: sem mudança desde o parecer anterior (cartão ROTULO-VARIAVEL; recomendação 4 do review na abertura do PR).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática, `python3 -m unittest tests.test_hooks`, `git`, `forge-check delta`. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna; o delta não traz dependência, workflow nem segredo). O login do dono no `gh` falso não é segredo.
