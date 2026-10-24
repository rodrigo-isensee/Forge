---
tipo: revisao-seguranca
contrato: 1
pedido: release-dev-versao
branch: melhoria/release-dev-versao
commit: c3b7be0e97b98da13a35b3dddfa660fb3b0a979a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: release-dev-versao (rodada 2, volta 1)

Escopo: só o delta da volta. `forge-check delta --parecer` sobre o parecer anterior (commit `4805d77`) listou `bin/forge-changelog` (+26 -7; linhas 12, 88-114, 137, 144) e `tests/test_changelog.py` (138-180). Os commits são `b9a8208` (teste vermelho) e `c3b7be0` (correção). O que já estava aprovado no parecer anterior (a validação X.Y.Z da versão, a conferência do CI intacta) não foi reaberto. Fiz a revisão estática e sondas locais em `$TMPDIR/security-engineer-reldevversao2/`, com `HOME` próprio.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): a versão da release que o CI confere (`bin/forge-changelog release` grava a versão nos dois manifestos).

## Achados
- A1 (recomendado) bin/forge-changelog:113 · R1 entrou em parte. A validação é feita por json antes de gravar, mas a troca continua textual: uma chave aninhada antes da de topo, uma chave repetida ou uma aspa escapada no valor ainda dão rc=0, com o campo errado editado ou com JSON inválido gravado. A falha é fechada no pre-push e no CI.
- A2 (recomendado) bin/forge-changelog:122 · R2 entrou para os manifestos, mas não para o `CHANGELOG.md`, que ainda segue link simbólico e grava fora da raiz. Esse comportamento já existia antes desta mudança, e o delta não o cria.

## Detalhe dos achados
Conferência dos pedidos do parecer anterior:

1. **R1, validação por json antes de gravar: entrou em parte.** `ler_manifestos()` (`:88-107`) faz `json.loads` de cada manifesto e recusa com `sys.exit` quando o JSON é inválido, quando o topo não é objeto ou quando falta a `version` de topo como string. Isso acontece antes de qualquer escrita. Ficaram de fora duas coisas que R1 pedia: recusar a chave repetida (`object_pairs_hook`) e conferir, depois da troca, que `json.loads(novo_texto)["version"] == versao`. A troca de `:113` continua sendo `re.subn` só na primeira ocorrência. O histórico do pedido registra isso como suposição ("A4 só na leitura"). Resultado das sondas:
   - `{"engines": {"version": "9"}, "version": "0.1.0"}`: rc=0, a troca cai em `engines`, a de topo fica `0.1.0` e os fragmentos são apagados;
   - `{"version": "0.1.0", "version": "0.1.0"}`: rc=0, o json fica com `0.1.0`;
   - `{"version": "0.1\"x"}`: rc=0, e o regex `[^"]*` para na aspa escapada e grava `{"version": "0.2.0"x"}`, que não é JSON válido.

   Caminho de ataque: nenhum realista. É erro de edição que entra por PR revisado, e `test_versao_igual_a_do_forge` o barra no pre-push e no CI. Correção mínima (P, dono tech-lead): depois do `re.subn`, conferir `json.loads(novo_texto).get("version") == versao` e usar `sys.exit` se der diferente, ainda antes da primeira escrita. Para isso, a troca precisa ser calculada em `ler_manifestos` e devolver o texto novo. Isso cobre os três casos.
2. **R2, recusa de link simbólico e de caminho fora da raiz: entrou para os manifestos.** `:95-98` recusam o arquivo que é link, inclusive o quebrado (`exists() or is_symlink()`), e o caminho cujo `resolve()` sai de `Path.cwd().resolve()`. A recusa vale para o diretório `dev` como link, para `dev/.claude-plugin` como link e para `.claude-plugin` da raiz como link. Nos três casos as sondas deram rc=1, com o `CHANGELOG.md` intacto, os fragmentos mantidos e o alvo externo intacto. Um link de diretório que resolve dentro da raiz (`dev/.claude-plugin -> ../.claude-plugin`) é aceito e grava dentro do repositório. Isso não afeta a segurança. O `CHANGELOG.md` (`:122`, lido em `:123` e gravado em `:143`) ainda segue link: a sonda com `CHANGELOG.md` apontando para um arquivo fora da raiz deu rc=0 e gravou a seção `[0.2.0]` no alvo externo. R2 pedia "aplicar o mesmo ao `CHANGELOG.md`". Esse comportamento é anterior a esta mudança, e o peso é o mesmo do parecer anterior: o link aparece no diff e precisa de aceite do integrador. Correção mínima (P, dono tech-lead): a mesma checagem de `:97` para `CHANGELOG.md`.
3. **R3, nada pela metade: entrou.** `ler_manifestos()` roda em `:137`, antes da escrita do `CHANGELOG.md` (`:143`), da escrita dos manifestos e do `unlink` dos fragmentos. Os quatro testes novos (`tests/test_changelog.py:138-180`) conferem que, numa recusa, o `CHANGELOG.md`, o manifesto da raiz e o fragmento ficam intactos. Ainda pode sobrar estado parcial numa falha de E/S no meio das escritas, mas isso é informativo e se recupera com `git checkout`.
4. **Outro caminho de escrita fora do repositório: nenhum aberto.** O delta só escreve nos caminhos que `ler_manifestos` validou. Não entra caminho novo, nem variável de ambiente, nem argumento que vire caminho. A troca de `[^"]+` por `[^"]*` só passa a aceitar o valor vazio e não muda o alvo. O substituto continua sendo o X.Y.Z validado em `:118`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas:
- `forge-check delta --parecer`;
- leitura do diff `f50b9d4..c3b7be0`;
- `python3 -m unittest tests.test_changelog`: 35 OK, 1 pulado;
- `tests.test_forge -k test_versao_igual_a_do_forge`: OK;
- sondas locais em `$TMPDIR`: chave aninhada, repetida e com aspa escapada; links de arquivo, de diretório, da raiz, internos e do `CHANGELOG.md`.

Não estão no PATH e não foram instaladas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. O delta não traz segredo, dependência nem workflow.
