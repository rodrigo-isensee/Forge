---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-anexar
commit: f7f7f28fa5c798f7714b270a4d948ec8bd41b54c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-changelog-anexar (E1.262, parecer da E1.256)

branch: melhoria/v047-changelog-anexar · intervalo revisado: origin/develop (c5c3a449)..f7f7f28fa5c798f7714b270a4d948ec8bd41b54c

## Gatilhos
Toca `bin/forge-changelog` (classe C, sensível da catraca): o novo `release --anexar <versão>` lê e apaga arquivos de `changelog.d/` e reescreve `CHANGELOG.md`. Gatilho de R-SEGURANCA pelo lado de escrita e remoção de arquivo a partir de entrada de PR (o fragmento) e de não afrouxar as guardas que a `release` já tinha. Sem workflow, sem segredo, sem dependência nova, sem rede.

## Achados
- A1 (recomendado) bin/forge-changelog:265 · a escrita do CHANGELOG vem antes de apagar os fragmentos e não é atômica; se o unlink falhar no meio, rodar de novo duplica as linhas já anexadas. Mesmo padrão da release; integridade, sem atacante. Opcional: escrever em temporário e renomear.

## Sondas

## Detalhe dos achados
Conferido por leitura e execução (sondas num diretório temporário, com o binário do head f7f7f28f):
- **Mesmas guardas da release:** `anexar` chama `conferir_caminho` no CHANGELOG (bin/forge-changelog:249) e `conferir_pasta_de_fragmentos` antes de ler e apagar. Sondas: CHANGELOG como link simbólico, `changelog.d` como link para fora da raiz e fragmento como link para fora: as três recusadas com rc=1 e o alvo externo intacto (o unlink não alcança fora da raiz).
- **Tudo ou nada:** os fragmentos são todos validados por `ler_fragmento` antes de qualquer escrita; com um fragmento válido e outro de tipo inválido, rc=1, CHANGELOG sem mudança e nenhum fragmento apagado.
- **Injeção de cabeçalho pelo fragmento:** linha de continuação precisa começar com espaço, então `  ## [9.9.9]` vindo do fragmento fica indentada e não casa `^## `; não cria versão falsa nem desloca a fronteira da entrada. Sondado: rc=0 e a linha ficou dentro da entrada 1.0.0 como continuação.
- **Versão:** `re.fullmatch(\d+\.\d+\.\d+)` antes de montar a regex, e a regex usa `re.escape`; `1.0.0|.*` recusada. `--anexar` com `versao`/`data` posicionais é recusado.
- **Escopo da escrita:** só o corpo da entrada casada (`m.start(1)..m.end(1)`); não toca manifestos nem `[Não publicado]`. A busca de seções em `anexar_por_tipo` fica restrita às linhas da entrada.
- **Processo:** reabrir uma versão já publicada é decisão de fluxo do dono (E1.256 no pedido), não risco de segurança; quem roda é o mantenedor na própria cópia, e o resultado passa por PR com CI e pareceres.
- A1: severidade informativa; esforço P; dono `tech-lead`. Não bloqueia (R-REVIEW).
- Testes rodados: `tests.test_changelog` (87 OK) e `forge-mutante tests/mutantes/v047-changelog-anexar-3.json` (M17 morreu em bin/forge-changelog:265). Suíte inteira só no CI; sem PR ainda (conferir o CI verde no PR).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura, testes e sondas locais; varredura de segredos fora do PATH (lacuna registrada), sem efeito aqui (diff sem segredo nem dependência).
