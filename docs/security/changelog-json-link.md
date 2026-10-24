---
tipo: revisao-seguranca
contrato: 1
pedido: changelog-json-link
branch: melhoria/changelog-json-link
commit: 705d5a9a4716adb692a3f19b31bde0bae0dfa494
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: changelog-json-link

Escopo: o diff `d150ec8...705d5a9`, com 4 commits (`80cf5bf` A1, `1acc698` A2, `e1ba013` fragmento, `705d5a9` teste) em 3 arquivos (`bin/forge-changelog`, `tests/test_changelog.py`, `changelog.d/changelog-json-link.md`). A entrega fecha os recomendados A1 e A2 de `docs/security/release-dev-versao.md`. Fiz a revisão estática e sondas locais em `$TMPDIR/security-engineer-cjl/`, com `HOME` próprio e repositórios descartáveis.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): a versão da release que o CI confere (`bin/forge-changelog release` grava a versão nos dois manifestos).

## Achados

## Detalhe dos achados
**A1 de release-dev-versao (troca da versão conferida por json): fechado.** `ler_manifestos` (`bin/forge-changelog:101-128`) calcula a troca (`:119`) e reparseia o texto novo com `object_pairs_hook` que recusa chave repetida em qualquer nível (`:88-92`, `:120-125`). Também confere `version` de topo `== versao` antes da primeira escrita, que fica em `:163`. Sondas (rc, efeito):
- chave `version` aninhada antes da de topo: rc=1, nada gravado e fragmento mantido;
- chave `version` repetida no topo (inclusive com o valor alvo) e chave repetida aninhada: rc=1, nada gravado;
- aspa escapada no valor: rc=1 ("geraria JSON inválido"), nada gravado;
- escape unicode na chave de topo (`version`), sozinho, com `version` aninhada depois ou com `version` aninhada antes: rc=1, nada gravado. A troca textual não acha a chave de topo, e a conferência barra;
- `version` literal mais `version` no mesmo objeto: rc=1 (chave repetida depois de decodificada);
- escape unicode no valor (`0.1.0`) e escape unicode numa chave aninhada: rc=0, com o topo correto;
- `"version"` dentro de uma string escapada: rc=0, com o topo correto e a string intacta;
- BOM UTF-8, comentário `//` e comentário `/* */` com `"version"` dentro: rc=1 (JSON inválido), nada gravado;
- topo que não é objeto: rc=1.

Não sobra caminho para a release gravar versões diferentes nos manifestos: cada manifesto só é gravado se o `version` de topo do texto exato que vai ao disco for igual à versão pedida.

Resíduo (recomendação, severidade baixa, sem caminho de ataque): `:119-124` com o manifesto que **já** está na versão alvo e tem uma chave `version` aninhada antes da de topo. A troca edita o campo aninhado, e a conferência passa porque o topo já é igual. Sonda: `{"x": {"version": "0.1.0"}, "version": "0.2.0"}` vira `{"x": {"version": "0.2.0"}, ...}`, com rc=0. As versões continuam iguais nos manifestos, então o controle do CI não é afetado. O dano é uma edição colateral, que aparece no diff do PR de release. Os manifestos atuais têm um único `"version"` cada. Correção mínima (P, dono tech-lead): trocar a conferência por `conferido == {**dados, "version": versao}`, que também recusa qualquer outra mudança.

**A2 de release-dev-versao (`CHANGELOG.md` sem link): fechado.** `conferir_caminho` (`:95-98`) é chamado em `:142`, antes da leitura e de qualquer escrita. Sondas:
- `CHANGELOG.md` como link para fora da raiz: rc=1, alvo intacto;
- `CHANGELOG.md` como link quebrado: rc=1, nada criado;
- `CHANGELOG.md` como link interno: rc=1 (mais estrito que o necessário, sem efeito colateral);
- `dev` como link de diretório, `dev/.claude-plugin` como link, `.claude-plugin` da raiz como link e `plugin.json` como link: rc=1, alvo externo intacto, manifesto da raiz e fragmento mantidos.

Resíduos (informativos, sem caminho realista):
- **Troca do link entre a checagem e a escrita.** `:142` e `:111` conferem, e `:133` e `:163` escrevem com `write_text`, que segue link. Explorar isso pede um processo local com escrita no repositório rodando durante a release. Quem tem esse acesso já edita os arquivos direto, então não ganha nada. Não vale `O_NOFOLLOW`.
- **Hard link.** Um `CHANGELOG.md` que é hard link de um arquivo de fora passa (sonda: rc=0, alvo externo alterado). O git não versiona hard link, então ele não chega por PR. Só existe se for criado à mão na máquina.

**Dimensão nova da matriz (fora do diff; recomendação, severidade baixa): `changelog.d` como link de diretório.** `fragmentos()` (`:58-59`) e o `unlink` (`:166`) não passam por `conferir_caminho`. Sonda: com `changelog.d` apontando para uma pasta fora da raiz, o resultado é rc=0. O conteúdo externo é publicado no `CHANGELOG.md` e os arquivos `.md` da pasta externa são **apagados**. Um fragmento que é link de arquivo só apaga o próprio link. O comportamento é anterior a esta entrega, e o peso é o mesmo do A2 anterior: o link chega por PR, aparece no diff e precisa do aceite do integrador. Correção mínima (P, dono tech-lead): aplicar `conferir_caminho` a `Path(PASTA)` e a cada fragmento antes da leitura em `:150-154`, mais um teste.

**A conferência de versão do CI não enfraqueceu.** `tests/test_forge.py:154` (`test_versao_igual_a_do_forge`) não está no diff e passa. `.github/workflows/ci.yml` e `conferir` (`:140-172`) não mudaram. A entrega só deixa a release mais estrita. Não há caminho novo, variável de ambiente nem argumento que vire caminho. O substituto `versao` continua validado como `\d+\.\d+\.\d+` em `:137`, e por isso não injeta referência de grupo no `re.subn`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas:
- leitura do diff `d150ec8...705d5a9` e de `bin/forge-changelog` inteiro;
- `python3 -m unittest tests.test_changelog`: 41 OK, 1 pulado;
- `tests.test_forge -k test_versao_igual_a_do_forge`: OK;
- sondas locais em `$TMPDIR/security-engineer-cjl/`: variações de JSON (aninhada, repetida, escape unicode, BOM, comentário, topo não objeto) e de link (arquivo, diretório, quebrado, interno, hard link).

Não estão no PATH e não foram instaladas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. O delta não traz segredo, dependência nem workflow. Os itens de `docs/engineering/achados-recorrentes.md` (PA-7) foram conferidos, e o bloco está vazio.
