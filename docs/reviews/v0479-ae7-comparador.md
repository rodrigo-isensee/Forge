---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 3d0bdaf9089fe91ae820e969846ba79234413809
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.36, AE7.1 `forge-check comparar`, revalidação no head 3d0bdaf9)

Revalidação (H3, R-REVIEW) do parecer aprovado em 5961e2f3 (E58.32). Delta lido por
`forge-check parecer delta docs/reviews/v0479-ae7-comparador.md`: intervalo `5961e2f3..3d0bdaf9`, no domínio
`bin/forge-check`, `bin/forge_comparar.py`, `changelog.d/v0479-ae7-comparador.md`, `tests/mutantes/v0478-ae7-comparar-{2..7}.json`
e `tests/test_comparar.py`. Fora do delta nada foi relido.

## Conferido
- A1 do review anterior (e A1 da segurança): veredito em 4 níveis (`recusa < pergunta < sem decisão < allow`), `allow` acima do
  silêncio; entre hooks do mesmo caso vence a recusa, depois a pergunta, depois o `allow` (`rodar_caso`, chave
  `(n == ACEITE, n)`). O `updatedInput` que muda entre os lados sai `aceite-novo ... entrada-reescrita`, com a raiz do projeto
  normalizada. Testes `DecisaoInteira` (sonda S1 incluída).
- A2 da segurança: a árvore sai por `ls-tree -r -z` e `cat-file --batch`, como o clone a instala (sem export-subst nem
  export-ignore); submódulo pulado; nome ou link que resolve fora da pasta, lote truncado e git que falha saem
  `nao-verificavel`; links criados por último, nenhum arquivo gravado através deles. Testes `ComoOClone` (sonda S2).
- A2 e A3 do review anterior (A3 e A5 da segurança): `medir` roda cada lado inteiro, em temporário e HOME próprios, a base
  apagada antes do head começar; base que não extrai não roda o head; `HOME` saiu da lista positiva do ambiente. Testes
  `LadosSeparados` (sonda S3).
- Teste do item: `python3 -I tests/test_comparar.py`, 42 testes OK em 9,6 s.
- Mutantes (V2): `bin/forge-mutante --processos 1` nas 7 specs, 49 de 49 morreram (CMP3 a CMP5 e CMP49 por erro do teste
  sob o mutante); `--cobertura --base 5961e2f3` sem guarda descoberta; `--conferir --base 821db42e`: trechos no lugar.
- Tamanho (H1): `git diff --numstat --no-renames origin/develop...HEAD` nos caminhos de código dá 196 adições e 1 remoção
  (197 linhas: `bin/forge_comparar.py` 190, `bin/forge-check` 5, `bin/forge-testes` 1+1). **Excesso justificado:** o item
  continua com um comportamento só (a medida "só aperta"); as 49 linhas a mais são as três correções que a segurança
  reprovou, e cada uma tem sonda em teste (S1 a S3) que fica vermelha sem ela, ou seja, cortar deixa a suíte vermelha, o
  critério do H1. A alternativa (mesclar 5961e2f3 e corrigir depois) poria na `develop` um comparador que dá `so-aperta:
  medido` falso contra um head adversário, pior que não ter a medida. O PR deve dizer `teto: excedido, 197 linhas, ...`
  (a contagem do H1 soma as remoções; o autor informou 196).
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A4 (recomendado) bin/forge_comparar.py:149 · só a raiz do projeto é normalizada nas reescritas; `HOME` e `transcript_path` são diferentes em cada lado, então um hook que os cite no `updatedInput` dá `entrada-reescrita` falso. Erro do lado seguro (falso aceite-novo); normalizar o HOME como `{home}`.

## Sondas

## Parecer
Aprovado no head 3d0bdaf9. O delta fecha A1 a A3 do parecer anterior e os bloqueantes da segurança com teste de
comportamento e mutante morto em cada guarda nova; o excesso do teto (197 linhas) é justificado pelo critério do H1. A4 é
recomendado (R-REVIEW): vira cartão depois do merge. A decisão sobre os bloqueantes da segurança é do `security-engineer`
(R-SEGURANCA), na revalidação dele.
