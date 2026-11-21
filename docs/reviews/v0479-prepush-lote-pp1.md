---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-lote-pp1
commit: 51648bfe12a049ce1ac0f2e15b1eed09c4e92c8e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E94.2, melhoria/v0479-prepush-lote-pp1)

Escopo: diff `fb3b670b..51648bfe` (proposta `docs/propostas/prepush-lote-pp1.md`, `tests/test_prepush_lote_pp1.py`, 5 specs de mutante, `bin/forge-testes`, `tests/pesos-d4.json`, `tests/test_reval_delta.py` e o fragmento). Suíte inteira: fica com o CI do PR (`R-REVIEW`), não rerrodada.

## Achados
- A1 (bloqueante) tests/test_prepush_lote_pp1.py:226 · O teste copia e roda o bin/forge-mutante real, mas grava o falso como f"bin/{MUTANTE}" e esconde o caminho do MapaCobreOQueOsTestesLeem (S1). Isso dribla um teste (R-CONFORMIDADE). Use o literal e ponha bin/forge-mutante -> test_prepush_lote_pp1 (e test_pre_push_patch) no MAPA.
- A2 (recomendado) docs/propostas/prepush-lote-pp1.md:67 · O comentário fala em "envio de código", mas a condição avisa em qualquer envio com a base e a lista vazia. Ajuste o texto ou a condição.

## Sondas
- S1 · cópia de 51648bfe com "bin/forge-mutante" literal no lugar de f"bin/{MUTANTE}", rodando MapaCobreOQueOsTestesLeem · espera: OK se o mapa cobrisse o executado · obtido: FAILED, bin/forge-mutante -> [test_forge, test_forge_mutante, test_indice_forge, ...]; com a variável, OK

## Parecer
Reprovado só pelo A1. O resto está correto.

- **Quatro cartões iguais ao E14:** o hook da `develop` (fb3b670b), que é o pai do 5fec4384, recebeu o `git apply` da proposta e foi comparado com `diff` ao hook do 5fec4384. A única diferença são os dois trechos do PREPUSH-FORGE-AVISO-LISTA-VAZIA. Os quatro primeiros cartões (texto da trava por fd, cobertura com a guarda de link do `forge-check`, índice e pulos, intervalo) são idênticos byte a byte, como o texto declara.
- **Intervalo 0 recusado:** concordo. O inválido já reprova hoje e `test_pre_push_fila` prova isso. Cair no padrão afrouxaria a recusa. O desvio do texto do cartão está declarado na seção 1, com a troca de duas linhas que o dono faz se preferir. O `10#` resolve `08` e `09`, e o `case` recusa antes da conta.
- **Aviso de lista vazia:** o `wait "$!"` lê a saída da substituição de processo (bash 5.2). A remoção de ref fica fora de `envios`, então apagar uma branch não dispara aviso falso. Com `afetados`, a lista ilegível leva à suíte inteira, o que aperta. O spec `v0479-prepush-lote-pp1.json` rodou com M1 a M8 mortos, incluindo M5 a M8 desta guarda.
- **Custo:** o envio só de texto continua igual (+20 ms). O envio de Python de controle soma de 0,4 a 0,5 s, sem teste, abaixo do teto de 3 s do critério de reversão.
- **Teste novo:** `tests.test_prepush_lote_pp1` passou, 33 testes OK em 14,9 s. O ambiente é limpo (`sem_git_herdado`) e os hooks rodam direto.
- **A1, por quê:** `CoberturaDaCatraca.preparar` copia `RAIZ/bin/forge-mutante` e o roda. Se o formato da saída de `--cobertura` mudar, o filtro da proposta e este teste quebram. Hoje `forge-testes --listar bin/forge-mutante` não aponta para este módulo. O comentário da linha 224 assume que "Mudar o forge-mutante roda este módulo só no CI", e a variável existe para o teste de cobertura do mapa não ver o caminho. Para corrigir: uma regra no MAPA de `bin/forge-testes` para `bin/forge-mutante`, com `test_forge_mutante`, `test_forge`, os leitores atuais, `test_prepush_lote_pp1` e `test_pre_push_patch`, e o literal no lugar da variável. A regra é exceção real à convenção, então `test_o_mapa_nao_repete_o_que_a_convencao_ja_acha` não a recusa.
