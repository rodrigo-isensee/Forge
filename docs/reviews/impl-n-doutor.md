---
tipo: review
contrato: 1
pedido: impl-n-doutor
branch: melhoria/impl-n-doutor2
commit: eb6db50ffddaa4d53e0aba23348b24b70d242b3c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-n-doutor

Etapa E1.2 do pedido `docs/pedidos/impl-n-doutor.md`. Esta instância não é a autora (D-ETAPAS-INST = A). A branch foi refeita: `melhoria/impl-n-doutor2`, base `a3dbe22` (develop atual), HEAD revisado `eb6db50`, quatro commits: `526ef0b` (62), `1f3bc73` (RELOGIO-WSL), `e4a82bc` (F8) e `eb6db50` (fragmento). Desenho: `docs/propostas/discovery-0.29.0/n-doutor.md`, §1 e §3, itens 1, 2 e 4. Modelo de ameaças: `docs/security/ameacas/n-doutor.md`.

## Achados

## Parecer
**Aprovado.** Os três itens entregues seguem o desenho e o modelo de ameaças. Cada commit se reverte sozinho no HEAD, e a suíte dos módulos afetados fica verde depois de cada reversão. Os dois achados do review antigo (`2f83824`) estão resolvidos.

**A1 e A2 do review antigo.**
- A1, commits que não se revertiam sozinhos: resolvido. Cada item agora tem trechos próprios no `bin/forge-doutor`: uma linha da docstring por item, as funções em pontos diferentes do arquivo (`conferir_relogio` em :213, `conferir_custo` em :281, `conferir_protecao_github` em :358) e uma linha própria no `diagnosticar` (:404, :408, :410). Os testes de cada item ficam num arquivo próprio: `tests/test_doutor_custo.py`, `tests/test_doutor_relogio.py` e `tests/test_doutor_protecao_gh.py`.
- A2, fragmento renomeado junto com um ajuste de teste: resolvido. O fragmento `changelog.d/impl-n-doutor2.md` nasce num commit só (`eb6db50`), já com o nome da branch. O ajuste da thread do teste do relógio entrou no próprio commit do RELOGIO.

**Sonda de reversão (P3 = B), feita à mão.** Para cada commit: um clone em `$TMPDIR`, checkout de `eb6db50` e `git revert --no-commit <c>` sozinho. Resultado: `ok 526ef0b`, `ok 1f3bc73`, `ok e4a82bc`, `ok eb6db50`, sem conflito. Confirma o PQ-5 do Jarvis.

Fui além do texto: depois de cada reversão, rodei os módulos `test_doutor*` e `test_atualizar` que sobraram. Os três deram `OK`. Os itens são independentes também no comportamento, e não só no texto.

**Os dois toques na Base de `tests/test_doutor.py`.** Os dois são ajuste de fixture, e nenhum deles testa o item:
- `526ef0b` (+3 −2, :17 e :67): tira do `self.env` herdado os nomes de `SINAIS_DE_CUSTO`. O desenho pede isso explicitamente (§1.1, "O que pode quebrar"), para que os testes de "tudo em ordem" não fiquem vermelhos em quem roda a suíte com algum desses nomes no ambiente. O mesmo filtro entra em `tests/test_atualizar.py:64` e em `tests/apoio_versao_defasada.py:26`. A lista fica em `tests/ambiente_git.py:16`, um módulo auxiliar. Sem o item, o filtro é inócuo.
- `e4a82bc` (+27 −3, `GH_FALSO` em :28): troca o `gh` falso por um que responde por endpoint e, por padrão, mostra as três branches protegidas. Sem isso, os testes do modo completo que já existiam ganhariam o "não consegui conferir" da F8. O `gh` antigo saía com 0 e sem texto, e o `repo view` não teria JSON. Os comandos que o falso novo não reconhece continuam saindo com 0 e sem texto, como antes. Por isso, sem o código da F8 (reversão do `e4a82bc` sozinho), a Base nova continua compatível, e a sonda acima prova isso.
- Os casos de teste de cada item estão nos arquivos próprios. Não há asserção de item na Base.

**Mérito.** O código de `bin/` e `hooks/` é idêntico ao do `47d20da`, já revisado no mérito sem defeito (conferi com `git diff --stat 47d20da eb6db50 -- bin hooks/doutor.py`, que dá vazio). Reconferi item por item:
- **62** (`bin/forge-doutor:267-298`): a lista é fixa, e o código só confere se o nome está presente. Nunca lê o valor nem executa o `apiKeyHelper`. Variável vazia ou só com espaço conta como ausente. O `ler_json` (:50) só aceita arquivo regular de até 1 MiB e abre sem bloquear. Cada fonte falha sozinha. O nome da chave de API não aparece em `bin/` nem em `hooks/` (P-A = A).
- **RELOGIO-WSL** (`bin/forge_versoes.py:182` e :200, `hooks/doutor.py:117`):
  - O `HEAD` usa um cliente de baixo nível, sem redirecionamento, sem corpo, sem credencial e sem proxy do ambiente, com o certificado validado.
  - Só aceita host público na porta 443. O prazo é total, controlado pela thread.
  - Um `Date` sem fuso dá None. Acima do teto de 30 dias, também dá None.
  - A injeção `FORGE_RELOGIO_REMOTO` só vale com `FORGE_PERMITE_LOCAL=1`.
  - No hook, o aviso sai uma vez por dia, na chave `relogio` do cache, e só depois de uma consulta de versão que deu certo e não está desligada. A falha não marca o dia.
  - O sinal está certo: remoto menos local positivo quer dizer relógio atrasado.
- **F8** (`bin/forge-doutor:358`):
  - Roda só no modo completo e com o `gh` logado.
  - Só faz leitura, com `--method GET` em endpoints fixos.
  - Tem três estados: protegida, sem proteção e "não consegui conferir".
  - O 404 só vale como "sem proteção" com a mensagem de branch sem proteção e depois de o `repo view` responder.
  - O `nameWithOwner` é validado. `GH_HOST` ou URL fora de `github.com` dá "não consegui conferir".
  - A saída do `gh` nunca aparece no aviso.
  - O texto aponta a skill `ci-cd`, o que o §3 do desenho permite até o N-TPL ser mesclado.

**Ferramentas e testes**, numa cópia própria em `$TMPDIR`:
- No HEAD, `python3 -m unittest tests.test_doutor tests.test_doutor_custo tests.test_doutor_relogio tests.test_doutor_protecao_gh tests.test_atualizar` deu `Ran 173 tests in 81.532s`, `OK`.
- `python3 tests/catraca.py --modo regras --base a3dbe22... --head eb6db50...` saiu com código 0, sem violação (R-CUSTO).
- **Vermelho sem a mudança:** com `bin/` e `hooks/` da base `a3dbe22` e os testes do HEAD, os três módulos novos deram `Ran 45 tests`, `FAILED (failures=36, errors=31)`. Os que ficam verdes na base são guardas de ausência, como já registrado no review antigo.
- A suíte inteira roda no pre-push deste envio.

**O M11 não entrou.** O autor parou pela regra de parada: não há cache de plugin nesta máquina, e o passo 0 do desenho (§1.4, ler o formato real do cache) é pré-condição para seguir. O próprio desenho manda não seguir sem ele, e o modelo de ameaças diz que o M11 sem o passo 0 não é revisável. A parada foi correta.

O que isso significa para a entrega:
1. Esta branch cumpre só três dos quatro itens do E1. O E1 do pedido **não** está completo.
2. Nada no diff finge o M11. O fragmento e as mensagens de commit citam só 62, RELOGIO-WSL e F8. O `bin/forge-atualizar` não foi tocado.
3. Este review aprova o que foi entregue e não corta o M11 do escopo. Antes do merge (E1.5), o corte precisa de uma decisão: pergunta ao dono na pré-entrega ou o cartão M11-CACHE (R-DECISAO). O PR não pode declarar o E1 inteiro feito.
4. Quando o M11 vier, entra como um commit próprio sobre `bin/forge-atualizar` e `bin/forge_versoes.py`, com testes num arquivo próprio. Nenhum dos três itens daqui depende dele.

**Recomendações** (não bloqueiam):
- `SINAIS_DE_CUSTO` aparece em dois lugares, `bin/forge-doutor:267` e `tests/ambiente_git.py:16`. Um teste que compare as duas listas evita que elas se separem em silêncio.
- `bin/forge-doutor:345`: o `r.get("enforcement", "active")` trata o campo ausente como ativo. O endpoint `rules/branches` só devolve regras ativas e não traz esse campo, então o padrão faz sentido. Convém um comentário no código dizendo isso. O ponto é do parecer de segurança.
- `bin/forge-doutor:361`: o `conferir_protecao_github` chama o `conferir_gh` de novo, e o modo completo faz dois `gh auth status`. Dá para passar o resultado do primeiro.
- `presente()` trata `CLAUDE_CODE_USE_BEDROCK=0` como presente. Isso gera um falso aviso raro, e o texto já diz "pode estar".

**Pareceres de outros papéis.** A segurança é parecer próprio do `security-engineer`, em `docs/security/impl-n-doutor.md` (E1.3), e não o refaço aqui. O diff não toca pipeline, contêiner nem IaC, então não há parecer de devops.
