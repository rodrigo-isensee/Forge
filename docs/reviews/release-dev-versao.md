---
tipo: review
contrato: 1
pedido: release-dev-versao
branch: melhoria/release-dev-versao
commit: 4805d77566dc567f0e9c9ed2bf62226df5a54947
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: release-dev-versao

## Achados
- A1 (bloqueante) bin/forge-changelog:93 · Correção: manifesto que não é JSON válido não falha; a sonda com `{"version": "0.1.0",` deu rc=0, gravou 0.2.0 no arquivo quebrado e apagou os fragmentos. Validar todos os manifestos com json.loads antes de gravar o CHANGELOG.md e sair com erro (sys.exit) nomeando o arquivo; teste vermelho do caso.
- A2 (bloqueante) bin/forge-changelog:95 · Correção: manifesto existente sem a chave "version" é pulado em silêncio (`if n:`); sonda com `{"name": "x"}` deu rc=0 e a release declarou sucesso sem gravar versão. Falhar alto (antes de qualquer escrita), conferir depois da troca que json.loads(novo)["version"] == versão; teste vermelho do caso.
- A3 (recomendado) bin/forge-changelog:96 · read_text/write_text convertem CRLF em LF (sonda: `{\r\n...}` saiu só com \n), contra o "sem mexer no resto do arquivo" da docstring; ler e gravar com newline="" preserva o final de linha.
- A4 (recomendado) bin/forge-changelog:94 · A regex troca o primeiro "version" do texto, não o de topo: sonda `{"deps": {"version": "9.9.9"}, "version": "0.1.0"}` trocou o aninhado. A conferência pós-troca do A2 fecha isso; hoje os dois manifestos têm "version" de topo na linha 3.

## Parecer
**Reprovado**, por dois bloqueantes da mesma classe (correção: falhar alto), que o brief pede explicitamente.

O que está certo: a release grava a mesma versão nos dois manifestos (`.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`), só nos que existem, sem criar o `dev/` (teste `test_sem_o_manifesto_dev_a_release_nao_cria_nada`); a troca por regex preserva ordem, campos, indentação e a quebra final em arquivos LF (o teste compara o texto inteiro do `dev/`); a docstring de uso foi atualizada; o fragmento `changelog.d/release-dev-versao.md` diz o mesmo que o código (dev e raiz). Commits limpos: `ea36987` teste vermelho, `4805d77` correção, Conventional Commits em português. `R-NEUTRO` e `R-CUSTO` sem impacto (só biblioteca padrão, caminhos da própria fábrica).

O que falta (A1, A2): `gravar_versao` roda depois de o CHANGELOG.md já ter sido reescrito, e não verifica nada: manifesto inválido ou sem "version" passa com rc=0 e os fragmentos são apagados, que é justamente a subida de versão silenciosa que o pedido quer eliminar (o `test_versao_igual_a_do_forge` só pegaria no pre-push, como na 0.29.0). Sugestão única para os dois: uma função que, para cada manifesto existente, carrega o JSON (erro nomeando o arquivo), calcula o texto novo e confere com json.loads que o "version" de topo ficou igual à versão pedida; rodar essa preparação antes de escrever o CHANGELOG.md e só então gravar tudo. Testes vermelhos: manifesto inválido e manifesto sem "version", ambos com rc != 0, CHANGELOG.md e fragmentos intactos.

## Evidência
- `python3 -m unittest tests.test_changelog`: `Ran 31 tests ... OK (skipped=1)`; `tests.test_forge -k test_versao_igual_a_do_forge`: `Ran 1 test ... OK`.
- Sondas em `$TMPDIR/tech-lead-reldevversao/` (HOME próprio, repositório descartável): inválido rc=0; sem "version" rc=0 e arquivo intacto; CRLF virou LF; "version" aninhado trocado no lugar do de topo.
- Ferramentas (shellcheck, validação do plugin, suíte completa): citadas pelo pre-push do autor (suíte 1792 OK no histórico do pedido), não refeitas aqui.
