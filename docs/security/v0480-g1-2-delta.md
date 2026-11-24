---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 55a57bdef7c790c1b35971abb8c1d91a6c89c3a3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478, G1.2 sozinho, volta por delta (E140.17)

Revalidação no head 55a57bde. A rodada anterior aprovou 41820406 e fica no git (f874c826).

Gatilhos: controles do Forge (`docs/regras/`), `PROTEGIDOS` (`bin/forge-check`).

## Delta lido
`forge-check parecer delta` cobre 41820406..55a57bde, sem o que veio da develop. No domínio aparecem `bin/forge-check`, `bin/forge-testes`, `agents/{qa-engineer,security-engineer,tech-lead}.md`, `docs/regras/R-{REVIEW,SEGURANCA}.md` e `tests/test_parecer_fora_do_delta.py`.
- `bin/forge-check:4130-4152` (`versoes_em_lote`) e `:4159`: as versões anteriores do parecer passam a ser lidas num só `cat-file --batch` em vez de um `git show` por versão. Cada versão é lida pelo tamanho do cabeçalho. Quando a versão foi apagada, o lote devolve `missing` e a versão sai None, como o show que falha. Saída truncada, fora do protocolo ou de um lote que falha dá None para essa versão e as seguintes, nunca um texto parcial. O nome com quebra de linha não vai ao lote. Uma versão ilegível vira `{}` e não é a rodada anterior. Sem rodada anterior, nada é recusado (`:4178-4179`), então a falha só deixa o bloqueante como está.
- `bin/forge-check:4182-4183`: se o parecer não tem bloqueante, a função sai antes de rodar o git. Isso equivale ao laço de `:4191-4205`, que só acrescenta recusa para `bloqueante`.
- `bin/forge-testes:218,251-253`: só a lista de testes muda (`test_fechar_limpar_clone`, que vem da develop, e o mapa das skills). Nenhum teste saiu.
- `agents/*.md` e `docs/regras/R-{REVIEW,SEGURANCA}.md`: são cortes de texto (fb9f4347, 55a57bde) e a receita de envio por caminho (#835, da develop). A receita `skills/briefs-e-conferencia/envio-de-parecer.md` mantém o `git add` do caminho explícito e proíbe `.` e `-A`. Nenhuma regra muda de sentido.

## Classificação
O delta é **neutro**: a decisão da checagem de pareceres não muda. A sonda de equivalência rodou sobre as 2105 versões de 1720 pareceres de `docs/{reviews,qa,security,devops}` deste repositório. O texto do lote saiu igual ao do `git show` antigo em todas, com 0 diferenças. O único desvio possível está num blob fora de UTF-8. Antes, o `git()` em modo texto levantava exceção; agora o blob é decodificado com substituição. Os campos que decidem (`pedido`, `branch`, `commit`) são ASCII, e nenhum caminho de ataque sai daí. Por isso fica sem achado. A classificação do item inteiro continua a da rodada anterior: afrouxa, por ordem do dono, no G1.2.

O `cat-file --batch` não lê nada fora do repositório. A sonda local, numa cópia temporária, testou `../segredo.txt`, o caminho absoluto e `docs/../../segredo.txt`, e os três deram None. O link simbólico devolve só o alvo como texto, como o `git show`. As refs vêm do `git log --format=%H` (hexadecimal), e o `rel` não passa de um caminho de árvore no objeto do repositório.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A branch está sem PR, e a suíte inteira fica para o CI. Rodei localmente só os testes dos arquivos tocados, `test_parecer_fora_do_delta` e `test_testes_tocados`: 225 testes, OK, 1 pulado. Ferramentas usadas: git, o `forge-check` do head e duas sondas locais em Python, ambas só de leitura. Nenhuma varredura externa e nenhuma ferramenta instalada.
