---
tipo: revisao-seguranca
contrato: 1
pedido: release-dev-versao
branch: melhoria/release-dev-versao
commit: 4805d77566dc567f0e9c9ed2bf62226df5a54947
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: release-dev-versao

Escopo: `git diff db55859529da47652babded81461d2b0500ef79f...4805d77566dc567f0e9c9ed2bf62226df5a54947`, com os arquivos `bin/forge-changelog`, `tests/test_changelog.py` e `changelog.d/release-dev-versao.md`. Fiz a revisão estática e sondas locais com repositórios descartáveis em `$TMPDIR/security-engineer-reldevversao/`, com `HOME` próprio.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): a versão da release que o CI confere. `bin/forge-changelog release` passa a gravar a versão em `.claude-plugin/plugin.json` e em `dev/.claude-plugin/plugin.json`.

## Achados

## Detalhe dos achados
Conferências pedidas no brief:

1. **A versão não chega aos manifestos com espaço nem com prefixo `v`.** `release()` valida a versão com `re.fullmatch(r"\d+\.\d+\.\d+")` (`bin/forge-changelog:100`) antes de qualquer escrita, e `gravar_versao` só recebe esse valor. A sonda recusou `v0.2.0`, `"0.2.0 "`, `" 0.2.0"` e `0.2.0\n` com rc=1, sem tocar em nenhum manifesto. A substituição `\g<1>{versao}\g<2>` (`:94`) não sofre injeção, porque a versão só tem dígitos e pontos. Espaço e quebra de linha em volta do `:` (`"version"  :\n "0.1.0"`) são tratados por `\s*`. Uma aspa escapada dentro de outro campo (`\"version\"`) não casa. Conforme.
2. **Chave `version` repetida, aninhada ou ausente.** Aqui os manifestos podem divergir, mas a divergência não passa pelo CI (ver R1). A troca é textual e vale só para a primeira ocorrência (`:94`, `count=1`). Resultados da sonda: com a chave repetida, o JSON fica com o último valor (o antigo); com um `"version"` aninhado antes do campo de topo (`engines.version`), a troca cai no objeto aninhado; sem a chave, o arquivo fica intacto. Nos três casos a release sai com rc=0 e os manifestos ficam com `raiz 0.2.0` e `dev 0.1.0` (ou `None`).
3. **Link simbólico em `dev/.claude-plugin/plugin.json` faz a release gravar fora do repositório.** A gravação segue o link (ver R2). `Path.exists`, `read_text` e `write_text` (`:91-96`) seguem o link do arquivo e o do diretório. A sonda gravou `0.2.0` num JSON fora do repositório nos dois casos: o arquivo `plugin.json` era um link, e depois o diretório `dev/.claude-plugin` era um link. O efeito fica limitado: troca o primeiro `"version": "..."` do alvo por um X.Y.Z validado. O mesmo já valia para o `CHANGELOG.md` antes desta mudança.
4. **A conferência de versão do CI não fica mais fraca.** O diff não toca em `tests/test_forge.py`, `tests/config.json` nem nos workflows. `test_versao_igual_a_do_forge` (`tests/test_forge.py:154-155`) segue comparando os dois manifestos por `json` (último valor da chave, `KeyError` se ela faltar). O teste de `tests/test_forge.py:96-97` segue comparando `.claude-plugin/plugin.json` com a última versão do `CHANGELOG.md`. Os três casos do item 2 falham nesses testes, no pre-push e no CI (falha fechada). A mudança automatiza o que antes era manual e não dispensa nenhuma conferência. Com o worktree no commit revisado, `tests.test_changelog` deu 31 OK (1 pulado) e `test_versao_igual_a_do_forge` deu OK.

Recomendações (não bloqueantes):

- **R1 (baixa) `bin/forge-changelog:94`:** a troca textual, só na primeira ocorrência, pode editar o campo errado ou nenhum, e a release ainda sai com rc=0. O caminho realista é um erro de quem edita o manifesto, não um ataque: um campo aninhado `version` ou uma chave repetida entra por PR revisado. O que se perde é tempo, porque o defeito só aparece no pre-push ou no CI, e ninguém ganha acesso. Correção mínima, antes de gravar o `CHANGELOG.md`: ler cada manifesto com `json.loads(..., object_pairs_hook=...)` e recusar (`sys.exit`) se a chave de topo `version` faltar, se aparecer repetida ou se o topo não for objeto. Depois da troca, conferir que `json.loads(novo_texto)["version"] == versao`. Esforço P. Dono: tech-lead.
- **R2 (baixa) `bin/forge-changelog:91-96`:** a release segue link simbólico e grava fora da raiz. Caminho de ataque: um PR aceito na `develop` com `dev/.claude-plugin/plugin.json` (ou o diretório) como link (modo git 120000) para um arquivo do usuário que roda a release. `test_dev_so_tem_manifesto_e_agentes` (`tests/test_forge.py:167-173`) usa `is_file()`, que segue o link, e por isso não o pega. Pesa contra a probabilidade: o link aparece no diff, passa pelo code review e precisa ser aceito pelo integrador. O ganho do atacante é mínimo: trocar uma string de versão por X.Y.Z num arquivo que já tenha `"version": "`. Correção mínima: recusar quando `caminho.is_symlink()` ou quando `caminho.resolve()` não ficar sob `Path.cwd().resolve()`, e aplicar o mesmo ao `CHANGELOG.md`. Esforço P. Dono: tech-lead. Opcional: o teste de `dev/` recusar links.
- **R3 (informativa) `bin/forge-changelog:124-125`:** o `CHANGELOG.md` é gravado antes dos manifestos. Uma falha de escrita num manifesto deixa o estado parcial (seção nova gravada e fragmentos mantidos), e repetir a release dá "já tem a versão". A recuperação é `git checkout`. Com R1, validar tudo antes da primeira escrita resolve.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `python3 -m unittest tests.test_changelog` (31 OK, 1 pulado), `tests.test_forge -k test_versao_igual_a_do_forge` (OK) e sondas locais em `$TMPDIR` (versões inválidas, chave repetida, aninhada e ausente, link de arquivo e de diretório). Ausentes do PATH, e não instaladas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. A mudança não traz segredo, dependência nem workflow.
