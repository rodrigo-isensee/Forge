---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-prepush-patch
commit: d3bd84fbb90e92c08dbb0022d00ccc466d93331a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (patch dos três consertos do envio, E2.321)

Revalidação por delta (E2.507) do head d3bd84fb, depois do merge da develop (3a309e34). O `forge-check parecer delta` lista no domínio só `bin/forge-mutante` (116 linhas). Conferido por `git diff`: contra a base 86ac0fcb a branch só difere na docstring (3 linhas, já aprovada); o restante (`--conferir --todas`, `texto_no_commit`) veio da develop (94736f93, #594) e é do item dela. `docs/devops/pp1-pre-push.patch` não mudou desde 5016852d, e o `tests/test_pre_push_patch.py` roda 12 testes OK. Parecer segue aprovado; A1 e A2 seguem recomendados, sem mudança. A suíte inteira roda só no CI do PR.

Revalidação por delta (E2.368) do head 5016852d. O parecer anterior aprovou o head 805a0a10. O `forge-check parecer delta` lista, no domínio, `bin/forge-mutante` (só a docstring) e `tests/test_pre_push_patch.py`. O `docs/devops/pp1-pre-push.patch` mudou no mesmo intervalo, mas o delta o classifica como documentação. Como ele é o próprio controle do envio, foi relido inteiro.

A mudança troca o pré-filtro por prefixo do envio leve por um filtro da saída do `forge-mutante --cobertura`. O filtro usa a mesma lista da catraca do CI: `motivo_de_controle` e `TESTE`, as mesmas de `tests/catraca.py:835-843`. A guarda não afrouxa. A cobertura local agora alcança a classe C inteira (`.githooks/`, `.github/`, `.claude-plugin/`, `dev/`, `migrations/`, apoios e testes de controle). Antes, ela parava em `hooks/`, `bin/`, `scripts/` e `templates/projeto/`. O CI continua como portão. Parecer aprovado. A1 encolheu e A2 mudou de forma. Os dois seguem recomendados.

## Gatilhos
`R-SEGURANCA`: o patch muda um controle do Forge (o hook de envio, `R-VERIFY`, `R-FLUXO`) e executa código do repositório no envio.

## Achados
- A1 (recomendado) docs/devops/pp1-pre-push.patch:68 · o envio leve ainda pula o arquivo apagado (o teste -f do laço de controle): um diff que só apaga Python de controle não chama a cobertura, e a catraca reprova a condição apagada; não afrouxa, porque o CI confere
- A2 (recomendado) docs/devops/pp1-pre-push.patch:35 · exceção não tratada no forge-mutante sai com 1 sem linha de falta; o filtro devolve 0 e o envio passa calado, sem o aviso; não afrouxa (o CI é o portão); sair com 2 quando a saída 1 não traz nenhuma linha de falta

## Sondas
- S1 · filtro do patch com a entrada `Traceback (most recent call last)` e `KeyError: x` · espera: 2 (aviso) · obtido: rc=0, saída vazia
- S2 · filtro com `sem mutante · hooks/h.py:3 · if a` · espera: 1 · obtido: rc=1, a linha impressa
- S3 · filtro com `sem mutante · tests/test_x.py:3 · if a` · espera: 0 (teste fora da catraca) · obtido: rc=0
- S4 · filtro com `sem mutante · .githooks/x.py:3 · if a` · espera: 1 (fora do pré-filtro antigo) · obtido: rc=1

## Detalhe dos achados
**O que mudou no patch desde 805a0a10.**
- `texto_da_trava` (patch:9-14): a conferência `[ -e /proc/self/fd/9 ]` saiu. Sem o descritor, o `head` falha, o erro vai para `/dev/null` e o texto sai vazio. O texto só informa, então a falha continua fechada, como no parecer anterior.
- `COBERTURA_FILTRO_PY` (patch:24-46): roda com `python3 -I`, o que atende o AR-5. Ele importa `tests/catraca.py` por `sys.path.insert(0, "tests")`. O caminho é relativo, mas o hook faz `cd` para a raiz do repositório (`.githooks/pre-push:209`). Esse código é da própria branch, com a mesma confiança do `bin/forge-mutante` e do `bin/forge-changelog`, que o hook já executa. A lista é positiva (`motivo_de_controle`), sem lista negativa (AR-3). Uma falha ao carregar a catraca sai com 2, e isso vira aviso. Uma linha de falta que o filtro não consegue ler também sai com 2. Só as faltas filtradas chegam ao terminal, sem caracteres de controle.
- Um nome de arquivo com `:<dígitos>` no meio corta o caminho cedo no regex `(.+?):\d+`. O efeito é só no aviso local de quem escreve a própria branch, e o CI analisa por arquivo. Não há caminho de ataque.
- Laço `controle` (patch:66-69): agora qualquer Python do diff chama a cobertura, e é o filtro que decide. Isso alarga o que o laço anterior pegava.

**A1, em detalhe.** O pré-filtro estreito do parecer anterior foi resolvido pela lista da catraca. Resta o `[ -f "$arquivo" ]` do laço. Quando o diff só apaga Python de controle, o laço não marca `controle=1` e a cobertura não roda. A catraca do CI reprova a condição "apagada". Caminho de ataque: nenhum, porque o envio local não é portão e o CI do PR roda a catraca. Correção mínima: contar no laço também o arquivo que existia na âncora e sumiu (`git cat-file -e "$ancora:$arquivo"`), ou chamar a cobertura sempre que o diff tiver arquivo da classe C. Severidade informativa, esforço P, dono `devops-engineer`.

**A2, em detalhe.** No head 805a0a10, a exceção não tratada (fora de `RuntimeError`, `ValueError`, `OSError` e `SyntaxError`, `bin/forge-mutante:730`) saía com 1 e barrava o envio com o motivo errado. Agora a saída 1 passa pelo filtro. O traceback não começa com nenhuma de `FALTAS_DE_MUTANTE`, então o filtro devolve 0 e o envio segue sem aviso nenhum (S1). Não é afrouxamento: antes do patch não havia checagem local, e o CI continua a reprovar. Mas um erro da ferramenta passa calado. Correção mínima, no filtro: quando nenhuma linha da entrada começa com `FALTAS_DE_MUTANTE`, sair com 2, o que mostra "não conferiu o delta (saída 2)". Outra opção, no `forge-mutante`: capturar `Exception` em `main` e devolver 2. Severidade baixa, esforço P, dono `devops-engineer`.

**Fora do meu domínio:** a docstring de `bin/forge-mutante:68` foi atualizada, e a nota AR-9 do parecer anterior está resolvida.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Tudo foi rodado no clone, no head 5016852d:
- `python3 -m unittest tests.test_pre_push_patch`: 12 testes OK em 17,0 s.
- `git apply --check` e `git apply` do patch sobre o `.githooks/pre-push` da base (1b88640e): passaram.
- `shellcheck` e `bash -n` no hook remendado: sem aviso.
- As sondas S1 a S4, com o filtro extraído do patch.

A suíte inteira roda no CI do PR, que ainda não existe ("sem PR" no brief), e o merge depende dela. A varredura de segredos não rodou: o diff não toca segredo e o `gitleaks` não está no PATH. A auditoria de workflow também não: o diff não toca workflow.
