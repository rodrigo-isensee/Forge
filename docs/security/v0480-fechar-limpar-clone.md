---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-limpar-clone
commit: 7ba9f0bac3d84e0b231995b8e50778404b0ca179
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E132.12, PR #831: E132.6, E132.7 e E134.2 no forge-fechar)

Lido o diff inteiro `0ed441e9..7ba9f0ba` (base: o pai `0ed441e9` do merge da develop; 19 arquivos, código só em `bin/forge-fechar` e no mapa de `bin/forge-testes:218`). Os commits seguintes no remoto (`da29e998`, `1f5c0a3b`) só gravam os pareceres de QA e de review.

Gatilhos: controle do Forge (`bin/forge-fechar`, integrador que apaga branch, remota e clone), `git fetch` e `ls-remote` da origin, `rm -rf` de pasta em `~/.forge-contrib/wt`.

## Só aperta ou neutro, por escrito
- **Recusa da branch de integração (E134.2), aperta:** `bin/forge-fechar:180` troca `[cç][aã]` por `(c|ç|Ç)(a|ã|Ã)`. É a correção mínima do A1 do parecer da E134.1 (commit `38cd0504`). Em locale de byte único (C, POSIX ou locale não instalado, que cai em C), a recusa passa a valer. Em UTF-8 casa as mesmas linhas de antes, então lá é neutro. A lista fixa (`:175`) não muda.
- **`--principal` (A2 do review E132.2), aperta:** o valor vazio (`:125-126`) e a combinação com `--promover` (`:162`) ou `--limpar` (`:174`) viram erro de uso antes de qualquer passo.
- **`buscar_de` por metades (A1 do review E132.2), neutro:** cada sha buscável ainda é buscado. A metade que falha se divide até ficar com um sha só, e o fetch continua só de leitura (`--no-tags --no-write-fetch-head --no-auto-maintenance`, `:592`), preso ao sha40. Só cai o número de fetches.
- **Campo `clone=` sempre presente (`:831`), neutro:** só muda o texto da saída.
- **`limpar_clones` (E132.6), neutro para a garantia guardada:** o conjunto de clones apagados cresce, mas só com clones cujo conteúdo a origin já tem. As outras condições continuam todas exigidas: uma worktree só, `status` limpo (inclui arquivo novo), stash e commit fora da origin. Os dois afrouxamentos são estes:
  - **Commit fora das refs remotas velhas do clone (`:628-632`):** vale como "na origem" só se as pontas lidas agora da origin (`ls-remote` de `refs/heads/*` e `refs/tags/*`, `:264-270`) o alcançam. A conta roda nesta cópia, depois da busca só de leitura (`:606-611`). Em três casos o resultado é `erro` e o clone fica: a leitura da origin falha (pontas vazias), o commit é só do clone (esta cópia não o lê) ou uma ponta não se lê. O clone não roda fetch: o `.git/config` dele, gravável, não ganha execução.
  - **HEAD ancestral de um head mesclado (`:633-634`):** só substitui a exigência de sha igual. Não dispensa as checagens de trabalho fora da origin.
- **Testes e mutantes (E132.7):** nenhum teste afrouxou. `test_lsremote_exato_um_ajudante_unico_le_a_branch_remota` está igual ao da base. As asserções tocadas ganharam ` clone=nenhum` e a variante com locale foi somada. Os mutantes M12 e M13 de `v0474-mp6-disco-2.json` e o M5 de `v0480-fechar-busca-pareceres.json` só acompanham o texto novo da guarda; o M5 ganhou mais um teste.

## O --limpar nunca apaga trabalho fora da origem
Sondas em ambiente descartável (o mesmo de `tests/test_fechar_limpar_clone.py`, `LC_ALL=C`). As quatro deram o resultado esperado, com o clone mantido, código 3 e `clone=pendente`:
- **Objeto local nesta cópia:** o commit não enviado do clone foi trazido para esta cópia por fetch sem ref. O objeto ser legível não o torna "na origem", porque a conta é de alcance a partir das pontas da origin.
- **Commit em outra branch do clone:** HEAD ancestral do mesclado, com um commit não enviado em outra branch local.
- **Tag de blob na origin:** tag que aponta para um blob, mais um commit local não enviado.
- **Stash:** HEAD ancestral do mesclado, com stash.

Os testes do PR cobrem a leitura da origin que falha (o clone fica) e a busca que não cria ref nesta cópia.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas:
- **Testes dos arquivos tocados no head:** `tests.test_fechar_longas`, `test_fechar_limpar_clone` e `test_fechar_busca_pareceres` deram 21 OK, tanto em `LC_ALL=C` quanto em `C.UTF-8`. `test_fechar`, `test_forge_fechar`, `test_fechar_config`, `test_fechar_orfao`, `test_fechar_prune_sandbox`, `test_fechar_r1_worktree`, `test_fechar_sha_arvore` e `test_fechar_sinal` deram 188 OK (1 pulado).
- **Mutantes:** `forge-mutante` matou M7, M8 e M12 de `v0480-fechar-limpar-clone-2.json`.
- **grep do padrão novo:** casa `integração`, `INTEGRAÇÃO`, `Integracao` e `integraÇÃo` em C, POSIX e C.UTF-8, e também com locale inexistente, que cai em C.
- **Suíte inteira:** não rodou, porque o brief a pede sem suíte local. Vale o CI do PR #831. No head `7ba9f0ba` ele ficou incompleto (partes canceladas pela execução seguinte, `bateria (pareceres)` vermelha porque os pareceres ainda não existiam) e, na execução sobre `1f5c0a3b` (mesma árvore de código), está na fila. O CI verde é obrigatório para o merge.
- **`shellcheck`:** a `bateria (verificações longas)` do run 45311318404 acusou SC2100 em `bin/forge-fechar:532` (`st=sem-pass`). A linha é anterior ao PR (`28b46a15`), está fora do diff e não é de segurança. Fica com o dono do script.
- **Lacunas:** `shellcheck` e `gitleaks` não estão nesta estação.
