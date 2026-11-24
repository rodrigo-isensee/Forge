---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: c102d6403eeccd5c7dce72fd6ca72abdabb51d0a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 E162.16 (PR #846, revalidação por delta, última volta)

Delta lido: `forge-check parecer delta` de `191484ef..c102d640`. No domínio, só `bin/forge-mutante`: `par_com` (`bin/forge-mutante:433-438`), o campo `par` nos mutantes do `--cobertura` (`bin/forge-mutante:708`, `bin/forge-mutante:768`), a linha `onde` de `provar` (`bin/forge-mutante:980-996`) e o texto do uso (`bin/forge-mutante:16-19`). Fora do domínio, mas lidos porque provam a correção: `tests/test_forge_mutante.py` (S7 em `Execucao`, `par_com` em `Cobertura`) e os M20 a M23 da spec `-3`. Já lido nas rodadas anteriores (no git, `786cd40c`, `d8ee1052` e `18da2f16`): o resto do diff `0733715a..191484ef`.

Gatilhos: controle do Forge (ferramenta do portão de mutação).

Achados anteriores: A1 (`786cd40c`), corrigido em `d8ee1052`. A2 (`d8ee1052`), corrigido em `18da2f16`. A3 (`18da2f16`, recomendado, par-escudo), corrigido neste delta pela correção mínima pedida: a saída e a `coberta` nomeiam as duas linhas, o uso exige que as guardas cubram a mesma condição e a S7 virou teste (`test_par_escudo_que_morre_nomeia_as_duas_linhas`).

## Só aperta ou neutro
- Saída da rodada de 2 pares com `(par com <arquivo>:<linha>)`: aperta a visibilidade. O revisor passa a ver a linha da guarda-escudo no relatório e não só na spec. O veredito, o rc e a checagem `par_que_nao_sobrevive` não mudam: neutro na decisão.
- `coberta` do `--cobertura` com o par: o mesmo. O nome do par só entra no texto da linha. `cobrem` decide pelo `equivalente`, como antes, e a contagem não muda.
- Leitores da saída: `scripts/placar-mutacao.py:30` casa `^\S+ · <classe> · `, e o sufixo vem depois da classe. A contagem do placar não muda: neutro.
- `par_com` só lê texto. `texto.index(de)` vem guardado por `de in texto`, e o `de` ausente some da lista sem erro. Em `provar`, o arquivo vem de `ler_no_commit` no mesmo sha que `mutar` já leu e validou (um `de` uma vez, UTF-8): neutro.
- Spec de uma troca: `par` fica vazio, e a saída fica igual à de antes (`onde` sem sufixo): neutro.

## Detalhe
**Sondas refeitas no head c102d640.** Rodaram num repositório descartável do diretório temporário da sessão, com a fixture no molde de `Execucao` e os setups da rodada `18da2f16`. Nenhuma delas prova um bloqueante, por isso ficam aqui e não num bloco `## Sondas`.
- S7 (par-escudo, de=["if y > 500:","if x < 0:"], para=["if y < 500:","if x < -100:"], teste `limite(-5) == 0`). A rodada sai `M2 · morreu · lib.py:4 (par com lib.py:2)`, rc 0. O `--cobertura` (as guardas entram no diff) sai `coberta · lib.py:4 · tests/mutantes/s.json:M2 (par com lib.py:2) · declarado, não provado`, rc 1 pela linha 2 sem mutante (`de` curto, regra anterior). Antes saía `lib.py:4` sem o par. O escudo agora aparece no relatório. A separação semântica continua com quem revisa a spec, como o A3 previa.
- S8 (redundância legítima, [`if x < 0:`, `if x <= -1:`]). Sai `M2 · morreu · lib.py:2 (par com lib.py:4)`, rc 0. O recurso segue servindo ao uso dele.

## Riscos aceitos e ferramentas
Nenhum risco aceito e nenhum achado aberto. O teste do arquivo tocado, `python3 -m unittest tests.test_forge_mutante` no head c102d640, passou: 156 testes, OK. Rodou localmente; a suíte inteira roda no CI do PR #846. As sondas S7 e S8 usaram só a ferramenta local. O delta não tem segredo (revisão manual).
