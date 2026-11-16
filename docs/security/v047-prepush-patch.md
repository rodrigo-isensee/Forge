---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-prepush-patch
commit: 805a0a1048222c22dc60f847eb879b16069fbbd6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (patch dos três consertos do envio, E2.321)

Parecer completo (E2.326) do head 805a0a10 sobre a base 1b88640e. O diff tem três arquivos: `docs/devops/pp1-pre-push.patch`, `tests/test_pre_push_patch.py` e o fragmento do changelog. O `.githooks/pre-push` em vigor não muda: o dono aplica o patch. A pergunta do pedido é se algum conserto afrouxa. A resposta é não: os três apertam ou mantêm a guarda. Parecer aprovado, com duas recomendações.

## Gatilhos
`R-SEGURANCA`: o patch muda um controle do Forge (o hook de envio, `R-VERIFY`, `R-FLUXO`), a leitura de um arquivo de trava num diretório temporário e a execução de código do repositório no envio.

## Achados
- A1 (recomendado) docs/devops/pp1-pre-push.patch:36 · o pré-filtro do envio leve é mais estreito que a classe C do CI: fica fora Python de controle em .githooks/, dev/, .claude-plugin/ e .github/, e o arquivo apagado (o teste -f o pula); não afrouxa, porque o CI confere; alinhar ou registrar a lacuna
- A2 (recomendado) docs/devops/pp1-pre-push.patch:41 · exceção não tratada no forge-mutante (fora de RuntimeError, ValueError, OSError e SyntaxError) sai com 1 e o hook a lê como mutante faltando: barra com o motivo errado; falha fechada, só disponibilidade; separar o 1 de veredito do 1 de erro

## Sondas

## Detalhe dos achados
**Os três consertos, um a um.**
- PRE-PUSH-TEXTO-TRAVA-FD (patch:9-14): aperta. `texto_da_trava` passa a ler `/proc/self/fd/9`, e não o caminho `$trava`. Esse descritor é o que `trava_confere` já conferiu (do próprio usuário, não é link). Os três chamadores abrem o descritor 9 e o conferem antes da leitura: `.githooks/pre-push:118-119` no `--status`, e `:466-467` antes de `mostrar_fila` (`:501`) e de `avisar_trava_velha` (`:518`). A suíte roda com `9>&-` (`:637`) e não chama a função. Abrir `/proc/self/fd/N` reabre o mesmo inode pelo link mágico, sem resolver o caminho de novo, e começa no deslocamento 0. Trocar o caminho por um link depois da conferência já não desvia a leitura. Sem o descritor, o texto sai vazio. Esse texto só informa: com ele vazio, `pid` não casa `^[0-9]+$` e nada libera a trava nem pula a fila (`:516-525`). Os limites antigos continuam: 200 bytes e só imprimíveis (C-14). O hook já dependia de `/proc/self/fd/9` em `trava_confere`, então o patch não cria dependência de plataforma nova. O `stat` do mtime segue pelo caminho (`:520`), mas só alimenta um aviso.
- FILA-INTERVALO-ZERO (patch:58-60): aperta. A validação de dígitos continua antes. A aritmética `$((10#$intervalo))` só recebe dígitos, então não há injeção pela expansão aritmética. `0` e `00` são recusados. Sonda local: `0` e `00` recusados, `08` aceito como 8. Um valor acima de 2^63 transborda: ou é recusado ou vira outro positivo, e o intervalo só controla a frequência da linha da fila. Valor enorme já era aceito antes do patch, então não há regressão.
- PREPUSH-LEVE-COBERTURA-CATRACA (patch:31-48): acrescenta um bloqueio no envio leve, onde antes não havia nenhum. Só a saída 1 barra; as outras viram aviso, e o CI segue como portão (o mesmo padrão de `scripts/verificar-contribuicao.sh`, `:367-374`). O código roda como `python3 -I` (AR-5 atendido). `bin/forge-mutante` precisa ser arquivo regular e não link. A base é o sha de `refs/remotes/origin/develop` (`:272`) e chega por `git merge-base`, sem texto livre. A saída que vai ao terminal sai sem caracteres de controle. A confiança é a mesma de `bin/forge-changelog`, que o hook já executa: é código da própria branch, escrito por quem já pode escrever nela. Nada é removido nem relaxado no hook.

**A1, em detalhe.** A lista do `case` é: `hooks/*`, `bin/*`, `scripts/*`, `templates/projeto/*`, `tests/catraca.py` e `tests/neutralidade.py`. A classe C do CI (`bin/forge-check:1018-1031`, `motivo_de_controle`) vai além: os `PROTEGIDOS` e `SENSIVEIS` de `tests/catraca.py:46-49` (`.githooks/`, `.github/workflows/`, `migrations/`), `PLUGIN_E_APOIOS` (`.claude-plugin/`, `dev/`, `tests/apoio_*.py`, `tests/modelo_*.py`), `PIPELINE_E_INFRA` e os testes de controle. Os testes de controle o `forge-mutante` já exclui por `TESTE`. Há também o `[ -f "$arquivo" ]`, que pula o arquivo apagado, e a catraca reprova a condição "apagada". Caminho de ataque: nenhum. O envio local nunca foi portão desta checagem, e o CI do PR roda a catraca completa. A lacuna é só de aviso antecipado. Correção mínima: trocar o pré-filtro pela própria `--cobertura` (ela já ignora o que não é controle) ou cobrir os prefixos acima e o arquivo apagado. Severidade informativa, esforço P, dono `devops-engineer`.

**A2, em detalhe.** `cobertura()` (`bin/forge-mutante:728-733`) captura `RuntimeError`, `ValueError`, `OSError` e `SyntaxError` e devolve 2. Qualquer outra exceção (`KeyError`, por exemplo) sai com 1 pelo interpretador, e o hook a mostra como "condição mudada sem mutante declarado". Não há caminho de ataque: a falha é fechada e só atrapalha o autor. Correção mínima: no hook, só tratar como reprovação o 1 que vem com uma linha `sem mutante`, `só equivalente` ou `apagada` na saída; ou, no `forge-mutante`, capturar `Exception` em `main` e devolver 2. Severidade baixa (disponibilidade), esforço P, dono `devops-engineer`.

**Fora do meu domínio, para o `tech-lead`:** depois de aplicado o patch, a docstring de `bin/forge-mutante:68` ("nenhum hook, pre-push nem CI chama") fica desatualizada (padrão AR-9).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado no clone, no head 805a0a10: `python3 -m unittest tests.test_pre_push_patch`, 8 testes OK em 10,3 s, com o original falhando e o remendado passando em cada conserto. `git apply --check` do patch sobre o `.githooks/pre-push` da base (blob f9443600) passou. A análise estática de shell, sobre o hook original e sobre o remendado, passou sem aviso. Também rodou a sonda da aritmética do intervalo (0, 00, 08, 2^64, 2^63 e um número de 20 dígitos). A suíte inteira roda no CI do PR, que ainda não existe ("sem PR" no brief), e o merge depende dela. Não rodaram a varredura de segredos (o diff não toca segredo e a ferramenta não está no PATH) nem a auditoria de workflow (o diff não toca workflow).
