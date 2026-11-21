---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: f50171d232c95fa4562422bcda5f92a144a8a586
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.45, AE7.1 `forge-check comparar`, revalidação no head f50171d2)

Revalidação (H3, R-REVIEW) do parecer aprovado em 3d0bdaf9 (E58.36) e da rodada reprovada em bddae43f (E58.40, só pelo A5 de
neutralidade; parecer que ficou fora do remoto). Delta lido por `forge-check parecer delta docs/reviews/v0479-ae7-comparador.md`:
intervalo `3d0bdaf9..f50171d2`, no domínio `bin/forge_comparar.py`, `changelog.d/v0479-ae7-comparador.md`,
`tests/mutantes/v0478-ae7-comparar-{4,6,8,9,10}.json` e `tests/test_comparar.py`; o trecho `3d0bdaf9..bddae43f` já foi julgado na
rodada E58.40, e aqui foi lido o `bddae43f..f50171d2`. Fora do delta nada foi relido.

## Conferido
- A5 da rodada E58.40 (R-NEUTRO): o comentário da linha 154 diz "como o Claude Code lê a saída", sem nome de stack (339cf138).
  `python3 -I tests/test_forge.py Neutralidade NeutralidadeDoNucleo`, com ambiente limpo: 6 testes OK.
- A10 da segurança (hook fora do `hooks/hooks.json`): `fora_da_medida` dá `nao-verificavel` com a chave `hooks` em qualquer
  nível de `.claude-plugin/plugin.json` ou `marketplace.json` (chave escapada incluída, pelo `object_pairs_hook`), com
  manifesto que não se lê e com `hooks:` sem recuo num `.md` de qualquer pasta e caixa; `git grep` que falha (rc fora de 0 e 1)
  também sai `nao-verificavel`. Na árvore real (`origin/develop` e este head) a busca dá rc 1 e os dois manifestos não têm
  a chave, então a medida segue útil no Forge. Testes `HooksForaDoHooksJson` (sondas S12, S13), nos dois lados.
- A9 da segurança (reescrita contra recusa): `reescreve = h != RECUSA and ...`; reescrita da base contra recusa do head não
  conta. Teste `test_reescrita_da_base_contra_recusa_do_head_nao_conta`. Specs 4 e 6 (CMP27, CMP46, CMP47) seguem a guarda nova.
- Teste do item: `python3 -I tests/test_comparar.py` com ambiente limpo, 53 testes OK em 13,2 s.
- Mutantes (V2): `bin/forge-mutante --processos 1` nas specs 10, 4 e 6: 22 de 22 morreram (CMP26 e CMP31 por erro do teste sob
  o mutante); `--cobertura --base bddae43f`: guardas novas cobertas (linhas 86, 88, 90, 232, 233, 235; a 214 da base apagada);
  `--conferir --base 821db42e`: trechos no lugar.
- Tamanho (H1): `git diff --numstat --no-renames origin/develop...HEAD -- bin/` dá 244 adições e 1 remoção (245 linhas:
  `bin/forge_comparar.py` 238, `bin/forge-check` 5, `bin/forge-testes` 1+1); o delta desde bddae43f somou 21. **Excesso
  justificado:** segue um comportamento só (a medida "só aperta"); as linhas novas fecham A9 e A10 da segurança, cada guarda
  com teste de comportamento que fica vermelho sem ela (CMP61 a CMP67 mortos), o critério do H1. Sem A10, um head que declara
  hook no manifesto ou no cabeçalho de agente sairia `so-aperta: medido` sem rodar esse hook, pior que não ter a medida.
  O PR deve dizer `teto: excedido, 245 linhas, ...`.
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A4 (recomendado) bin/forge_comparar.py:191 · só a raiz do projeto é normalizada nas reescritas; `HOME` e `transcript_path` são diferentes em cada lado, então um hook que os cite no `updatedInput` dá `entrada-reescrita` falso. Erro do lado seguro (falso aceite-novo); normalizar o HOME como `{home}`.
- A6 (recomendado) bin/forge_comparar.py:90 · a busca `-i` de `hooks:` sem recuo vale para o `.md` inteiro, não só o cabeçalho YAML; um doc com linha "Hooks: ..." deixa o comparador sempre `nao-verificavel`. Erro do lado seguro (hoje rc 1 na árvore); limitar ao bloco entre os `---` iniciais.

## Parecer
Aprovado no head f50171d2. O delta desde bddae43f fecha o A5 (neutralidade) e os achados A9 e A10 da segurança com teste de
comportamento e mutante morto em cada guarda nova; o excesso do teto (245 linhas) é justificado pelo critério do H1. A4 e A6
são recomendados (R-REVIEW): viram cartão depois do merge. A decisão sobre os bloqueantes da segurança é do
`security-engineer` (R-SEGURANCA), na revalidação dele.
