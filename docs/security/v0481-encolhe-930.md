---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-encolhe-930
commit: 27641d2acf103093952590e8c9f6a23461d2864d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (encolher o #930, PR #936, E46.3)

1ª rodada completa sobre `8855671d..27641d2a` (32 arquivos, +49 -876): sai a leitura da grafia do Bash na raiz do Forge (`destino_opaco`, `checar_texto`, `colada_em_vigor`, `ref_inteira`, `NOMES_EM_VIGOR`, a recusa da linha sem leitura e a do `MOTIVO_EM_VIGOR` sem alvo em `barrar`); o erro interno fecha só no Write, Edit, MultiEdit e NotebookEdit (`hooks/conformidade.py:4582`, `not entrada.get("command")`). É o que o dono decidiu na E37.26 e na E46.1; o rótulo `afrouxa-regra` é do dono.

## Gatilhos
Gatilhos: hook de conformidade (controle que analisa entrada), afrouxamento de guarda.

## O que fica provado
- Caminho literal sem perda: a sonda `sonda_e463.py` roda a mesma entrada no hook da base (develop `8855671d`) e no do head. `ln -s`, `git rm`, `git checkout --`, `cp`, `mv` do manifesto, `sed -i`, `tee` no Bash e Write, Edit, NotebookEdit e o Write em `.git/hooks` dão rc=2 nos dois. Só mudaram `python3 -c` com o literal e `F=.githooks/pre-push; printf x > $F`, de rc=2 para rc=0. É a grafia que saiu por decisão.
- A retirada de `MOTIVO_EM_VIGOR in o_que` em `barrar` (`hooks/conformidade.py:4315`) não abre o literal: todo `caminho_barrado` do caminho de escrita (`:1875-1880`) passa `alvo=`, e `na_raiz_em_vigor` o pega. As chamadas sem alvo são o texto de interpretador (`:2175`, que saiu por decisão), o índice do git (`:2930`, que segue barrado pelo caminho da escrita, como mostra `git rm`) e o link (`:2059`, com o mesmo resultado na base: o hard link sai pela outra montagem).
- Projetos sem mudança: o diff só toca `GuardaDaProva` e `prova_fora_de_projeto`, que valem fora de projeto. A `Guarda` base está intacta.
- A proteção do ambiente nesta estação: `test -w` (uma chamada sem efeito) dá não gravável em `.githooks`, `.githooks/pre-push`, `.git/hooks`, `.devcontainer`, `.devcontainer.json`, `.claude-plugin` e `.claude-plugin/plugin.json` da raiz, e o `allowUnsandboxedCommands` está em `false`. Vale com S21-S25 de `docs/security/v0481-hook-raiz-forge.md`.
- `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge`: OK local (48 fixtures `raiz-forge-*`, com as do erro interno do Bash, que libera, e do Write, que bloqueia).
- CI do head `27641d2a` (run 46006738406): suíte 1-5, python 3.14, instalação, passos, verificações longas, teto de pulados, árvore e catraca verdes. Só `bateria (pareceres)` e o agregado `bateria` ficam vermelhos, porque R-REVIEW ainda espera os pareceres desta rodada.

## Detalhe dos achados
Nenhum bloqueante nem recomendado novo. Segue aberto, e com o dono, o A18 de `docs/security/v0481-hook-raiz-forge.md`: o `denyWrite` das cinco entradas está só em `.claude/settings.local.json`, que não é versionado, e não em `.claude/settings.json:23`. O PR não muda isso, e `docs/hooks.md:69` registra o limite: a estação sem esse `denyWrite` fica sem a guarda da grafia do Bash na raiz, também no erro interno do Bash. O arquivo está em vigor, então só o dono pode gravá-lo (E37.26).

## Riscos aceitos e ferramentas
A grafia do Bash na raiz fica com o sandbox do sistema operacional, por decisão do dono (E37.26 e E46.1). O PR não tem aceite de risco. Usei sondas locais e passivas: hook em pasta temporária e `test -w`. A suíte inteira ficou com o CI. Não rodei `gitleaks`: o diff não tem segredo nem configuração com credencial.
