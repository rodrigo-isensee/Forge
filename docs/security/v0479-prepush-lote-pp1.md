---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-lote-pp1
commit: 51648bfe12a049ce1ac0f2e15b1eed09c4e92c8e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E94.3, lote PP1 do pre-push do Forge)

Gatilhos: hook de envio do Forge (controle, arquivo travado; a entrega é proposta de diff que o dono aplica), R-VERIFY.

Escopo lido: `fb3b670b..51648bfe` (proposta `docs/propostas/prepush-lote-pp1.md`, `tests/test_prepush_lote_pp1.py`, mutantes, mapa do `bin/forge-testes`), o hook da `develop` nos pontos de uso de `sem_caminhos`, `alterados`, descritor 9 e `intervalo`, e o hook com o patch aplicado numa cópia descartável.

## Achados

## Sondas

## Detalhe dos achados
**Só aperta: sim.** Nenhum ramo novo do diff libera envio nem pula checagem que roda hoje:
- Checagens novas (cobertura da catraca, índice, pulos; proposta linhas 152-209) só põem `falhas=1`; ferramenta ausente, link ou saída diferente de 1 vira aviso, exatamente como o envio de hoje, que não as roda. Cada bloco zera `rc` antes de usar, e o bloco do changelog (hook remendado, linha 502) reatribui `ancora`, então o reuso das variáveis não muda a decisão dele.
- `sem_caminhos=1` pelo `sort` que falha (linha 63): o único leitor anterior é `afetados()` (hook da `develop`, linha 584), que com `sem_caminhos=1` cai na suíte inteira. Antes, `sort` falhando deixava a lista vazia com `sem_caminhos=0`, e `afetados` marcava `nada=1` (nenhum teste). Isso é aperto, não afrouxamento. `so_parecer` não lê a lista.
- O `wait "$!"`: num shell que não o suporte, o retorno diferente de zero marca a lista como ilegível, o que é falha fechada (o envio fica mais caro, não mais permissivo).

**Aviso de lista vazia com rc 0: aceitável.** Isso mantém a gravidade baixa da E82.3. O envio leve não roda teste por desenho (ENVIO-LEVE), e o portão é o CI obrigatório para o merge. A causa (sem `sort` ou sem `mktemp` no PATH) é o ambiente de quem envia, não uma entrada de terceiro. Quem controla o PATH já controla a máquina e não ganha nada que o `--no-verify` não lhe daria, e o CI barra igual. Barrar travaria estações sem o utilitário e não daria ganho de segurança. Com `FORGE_PREPUSH_SUITE=afetados`, a lista ilegível já leva à suíte inteira. A prova de que o aviso não libera está na sonda S4/S5 da proposta: com tudo no PATH, o erro de sintaxe segue `rc=1`. O aviso também aparece num envio sem diff contra a `develop`. Esse falso aviso é inofensivo.

**Trava por `/proc/self/fd/9` (A2 da c6): correta.** Todos os chamadores de `texto_da_trava` rodam com o descritor 9 já aberto e conferido: `--status` (hook da `develop`, linhas 118-125, `exec 9<` e `trava_confere`) e a espera (linhas 466-518, `exec 9>>` e `trava_confere`). O `head` herda o descritor dentro do `$(...)`, e `/proc/self` é o próprio `head`. Trocar o caminho por link depois da conferência já não desvia a leitura (S8). Sem o descritor, ou com o arquivo sem leitura, o texto sai vazio. O texto só alimenta exibição e o aviso de trava velha, e nada nele libera a trava nem pula a fila. Resta `avisar_trava_velha` lendo o `mtime` pelo caminho (`stat -- "$trava"`). Isso é só informativo e não tem caminho de ataque.

**Intervalo da fila: correto.** O `case` exige só dígitos antes do `10#`. Resultados conferidos: `0` e `00` recusados; `08` vale 8; `-1` e `1a` recusados; `18446744073709551616` e `9223372036854775808` (estouro para 0 ou negativo) recusados pelo `-gt 0`; variável ausente ou vazia continua 60. O valor inválido segue barrando, como hoje (o desvio do texto do cartão está justificado na proposta, linha 18, e é o lado seguro).

Observação sem achado: o bloco da cobertura confere `-L` em `bin/forge-mutante` e `bin/forge-check`, mas não em `tests/catraca.py`, que o bloco dos pulos confere. A catraca é conteúdo da própria branch, executado na máquina de quem envia, com a mesma confiança dos testes. Não há caminho de ataque, por isso não é achado.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.

Ferramentas e evidência:
- `git apply --stat` lista só `.githooks/pre-push`; o patch aplicou e passou em `bash -n`.
- `python3 -m unittest tests.test_prepush_lote_pp1`: 33 testes OK (o teste de abuso novo).
- Sonda da seção 5 reexecutada contra o hook remendado: S1 a S8 reproduziram a saída declarada.
- Lacuna: o shellcheck não está no PATH desta estação; o CI o roda.
- Suíte inteira: só no CI do PR, que não foi citado no brief e não foi rodado aqui. O merge depende do CI verde.
