---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-autorizacoes-fixas
commit: 4c88ca81803e166767b3e3da3f3d4269e01ee305
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (AUTORIZACOES-FIXAS, E14.52; #901)

1.ª rodada completa (G1), diff contra a base comum com a `develop` (34ab6714). Etapa E14.65.

## Achados
- A1 (recomendado) bin/forge-fechar:1587 · seção de versão sem " - <data>" dá `ultima` vazia e passa como "não é de hoje" (sonda: "## [0.9.0]" sem data deu saída vazia). O forge-changelog sempre grava a data, então o risco é baixo; tratar vazio como erro fecha a falha.
- A2 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:185 · o F4 diz que a so-aperta-com-seguranca não libera o rótulo, mais estreito que a decisão do dono de 25/11 21:52. Correto agora, por R-CONFORMIDADE, mas citar o cartão ROTULO-SO-APERTA-PELO-TIME no F4 deixa a divergência à vista.

## Parecer
Aprovado no head 4c88ca81.

- ci: 4c88ca81803e166767b3e3da3f3d4269e01ee305 verde
- CI do #901 no head exato: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação, teto de pulados, árvore já provada e catraca verdes. Vermelhos só `bateria (pareceres)` (log: "R-REVIEW: PR toca bin/forge-fechar (e outros 2) sem parecer aprovado de review") e `bateria` (agrega "pareceres: failure"). Os dois esperam este parecer.
- Módulos tocados rodados aqui: `tests.test_autorizacao`, `tests.test_autorizacao_gravar` e `tests.test_fechar_corte`, 92 testes OK.
- Mutantes declarados (`bin/forge-mutante --processos 1` nas três specs v0481-autorizacoes-fixas*): M1 a M22 morreram. O M7 morreu por erro do teste declarado, o que ainda conta como morto.
- `shellcheck bin/forge-fechar`: só o SC2015 (info) da linha 674, que já estava antes e fica fora do diff.

Leitura:
- Faz o que a ordem de 25/11 07:52 pede. São dois atos fixos, com alvo `fixo` e validade `fixa` presos a eles nos dois sentidos (`limite` e `problemas` leem `adulterada` no cruzamento). Eles param só pela retirada `R-<Id>`. O vocabulário novo vale só para os atos fixos e não traz marca de negação nem de condição (há teste). Os termos de ato novos só fazem mais mensagens nascerem pendentes.
- O `--corte` abaixo do teto falha fechado. Ele exige ao menos 1 item, 06:00 locais ou mais, a última versão do CHANGELOG da develop de outro dia (erro de leitura conta como recusa) e a saída do `forge-check autorizacao ler --ato corte-diario` na forma positiva exata, ancorada na string inteira. A autorização usada fica no corpo do PR da marca. A marca segue em rascunho para a develop, com os pareceres e o `--laco` de sempre.
- O rótulo continua ato do dono. Nenhum código consome a `so-aperta-com-seguranca` (o único leitor de `Ato` novo é o `cmd_corte`, filtrado em `corte-diario`). O F4 tira dela o rótulo, o merge na main e o `R-CUSTO`. Os atos `rotulo-afrouxa-regra` e `merge-main` não mudam e leem `adulterada` com alvo `fixo` ou validade `fixa`. Isso está de acordo com a recusa do classificador e com `R-CONFORMIDADE`. A divergência com a decisão de 21:52 fica no cartão (A2).
- ADR: a emenda traz "Afrouxa?", "Por que o existente não basta", critério de reversão e uma tabela de leituras com medida (`R-DECISAO`). O F5 diz que a concessão fixa lê `adulterada` quando o plugin é atualizado, e isso é falha fechada.
- Tamanho (H1): cerca de 70 linhas de código, abaixo do teto. Os commits seguem Conventional Commits em português, um por mudança. O fragmento do changelog está presente.
