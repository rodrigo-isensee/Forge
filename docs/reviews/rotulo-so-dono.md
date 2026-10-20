---
tipo: review
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: 6ec509586c79014203222d65760177ab1be9674e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: o rótulo afrouxa-regra só do dono do Forge (E1.2, revalidação da volta 2)

Revisor independente (outra instância do `tech-lead`, D-ETAPAS-INST = A); o autor da E1.1, da E1.1v e da E1.1v2 não revisa. Este parecer substitui o anterior (aprovado sobre `b458a57`, citação corrigida em `2e5cc70`). Diff lido: só o delta da volta 2, `2e5cc70...6ec5095` (2 commits: `f494e90` hook; `6ec5095` testes e invariantes), 4 arquivos (`hooks/conformidade.py`, `tests/config.json`, uma fixture renomeada, `tests/test_hooks.py`). O que o delta não alcança segue como no parecer anterior.

## O que foi conferido
- **(a) B1 da segurança, crase escapada em `bash -c`, `sh -c` e `eval`:** a função nova `rotulo_no_argumento` analisa o argumento duas vezes, como veio e com `` \` `` trocado por crase (o que o shell de dentro executa). Isso cobre as três formas do B1 e o caminho que a segurança sugeriu. A troca também vale para o argumento entre aspas simples, onde o shell não tira a barra: ali sobra um falso positivo, mas para o lado fechado, e só quando a linha cita o rótulo (a conta do dono passa). Sondei com o harness de `tests/test_hooks.py` e `gh` falso de outra conta. Barram: `` bash -c 'echo \`gh pr edit 70 --add-label afrouxa-regra\`' `` (falso positivo esperado), `` eval echo \`…\` `` sem aspas e `bash -c` aninhado em dois níveis com a crase escapada.
- **(b) Recomendação 1 do parecer anterior, aspa simples em comentário:** `conteudos_de_crase` ignora `#` em início de palavra fora de aspas até o fim da linha, como faz o shell. Os casos `# don't` + crase na linha seguinte (com e sem aspas duplas) barram, e o caso `` echo a # `…` `` passa, o que está certo porque o shell não executa comentário. Sondei mais três formas, que barram: comentário depois de tab, comentário depois de `(` e `$'it\'s'` (ANSI-C) seguido de crase. Nenhuma forma achada esconde a crase.
- **(c) Recomendação 2, `gh label clone`:** exige a conta do dono sempre, com ou sem `--force`, porque pode criar o rótulo sem citar o nome. A frase de criação do `R-CONTRIB` já cobre o caso, então o texto da regra não muda.
- **(d) Recomendação 3, `--remove-label`:** `rotulos_removidos` (flag separada, `=`, lista por vírgula, caixa baixa) põe a remoção do rótulo sob a mesma exigência do `DELETE` em `issues/<n>/labels/<nome>`, e as duas formas do mesmo ato ficam coerentes. **A troca da fixture `remover-rotulo-libera` por `remover-rotulo-exige-dono` decorre diretamente deste item.** O comando é o mesmo (`gh pr edit 70 --remove-label afrouxa-regra`) e o `gh` falso sai com 1 (conta ilegível). O esperado passou de 0 para 2 com `R-CONTRIB`, ou seja, a mudança aperta e não afrouxa nada. As 12 fixtures `rotulo-so-dono-*` continuam lá. A exigência vai além do texto do `R-CONTRIB` (que fala em aplicar, criar ou renomear), mas para o lado fechado e com a explicação no docstring, então não é preciso mudar a regra.
- **(e) R5 da segurança, sessão de projeto:** `aninhado` repete a análise com `` \` `` trocado por crase. `test_rotulo_so_dono_volta_2_sessao_de_projeto` cobre as formas de (a) e (b) apontando para o Forge (barram com `R-CON…`) e as mesmas linhas sem o rótulo, que passam. A segunda passada só acrescenta recusas. Ela pode barrar uma linha com crase escapada que contenha uma ação crítica, o que mantém o lado fechado que o hook já tinha.
- **(f) Invariantes:** em `tests/config.json` entram `def rotulo_no_argumento`, `def rotulos_removidos` e `sub == "clone"`. A única linha `-` do diff é a mesma lista anterior, quebrada para receber a vírgula: todos os itens continuam lá e **nenhum invariante saiu**.
- **R6 (profundidade) e R1 (variável):** não estavam no escopo da volta. R1 segue no cartão ROTULO-VARIAVEL e R6 continua informativo no parecer da segurança.
- **Testes (item 11 do checklist):** dois métodos novos, com `minimo(casos, 20)` e `minimo(casos, 6)`. Eles cobrem as 11 formas que barram outra conta e passam com a conta do dono, mais 6 formas vizinhas que passam. Nenhum teste de ausência mudou de alvo.
- **Ferramentas (saída citada, não refeita):** `python3 -m unittest tests.test_hooks` nesta worktree, sobre `6ec5095`, deu `Ran 27 tests in 77.197s OK` (os 25 de antes e os 2 novos). A suíte completa (877 OK) e `scripts/validar-plugin.sh` (OK) são do autor, na E1.1v2.
- **Regras da fábrica:** `R-CUSTO`: nada pago, e `gh api user` continua só nas linhas que tocam o rótulo. `R-NEUTRO`: o login do dono aparece só no `gh` falso dos testes. O delta não toca a regra nem o fragmento `changelog.d/rotulo-so-dono.md`, nem `CHANGELOG.md` ou a versão. Os commits seguem Conventional Commits em português, um por mudança coerente (fix, depois test).
- **Segurança:** o parecer é do `security-engineer` (E1.3, revalidação em paralelo, `docs/security/rotulo-so-dono.md`). Está citado aqui e não refeito.

## Achados

## Detalhe dos achados
1. Recomendação 4 do parecer anterior, ainda de pé: o dono vem do `plugin.json`, não da URL do remoto como dizia o E2. Isso tem de ficar registrado no corpo do PR, como prevê a decisão técnica do Jarvis no pedido · severidade: recomendado.
2. `hooks/conformidade.py`, `rotulo_no_argumento` · a troca de `` \` `` por crase vale também dentro de aspas simples, onde o shell mantém a barra, e gera um falso positivo só na linha que cita o rótulo com outra conta. Não é risco: fica do lado fechado · nada a fazer agora; se incomodar, modelar as aspas do argumento original · severidade: recomendado.

## Pendências para o merge (não são do review)
- Rótulo `afrouxa-regra` aplicado pelo dono, na conta dele, depois do último push (a catraca exige isso por causa da mudança em `hooks/conformidade.py`).
- Sobreposição com o teto adaptativo em `tests/test_hooks.py` (anotada no pedido): o merge traz a `develop` antes; se o patch mudar, `forge-check pr` aponta o alcance da revalidação.
- Parecer de segurança da revalidação da volta 2 (E1.3) aprovado.

## Parecer
Aprovado: a volta 2 fecha o B1 da segurança e as recomendações 1 a 3 do parecer anterior, e estende a correção à sessão de projeto (R5). Toda mudança aperta o controle, nenhum invariante saiu e nenhuma outra regra muda. As duas recomendações acima não impedem o QA.
