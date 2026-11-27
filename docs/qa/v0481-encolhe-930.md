---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-encolhe-930
commit: 27641d2acf103093952590e8c9f6a23461d2864d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 encolher o #930 (PR #936, E46.4)

- ci: 27641d2acf103093952590e8c9f6a23461d2864d verde

`gh pr checks 936` no head: verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação`, `suíte` partes 1 a 5, `teto de pulados`, `árvore já provada` e `catraca`. Falham só `bateria` e `bateria (pareceres)`, que esperam este parecer (PARECER-LE-O-CI).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fica a recusa de Write, Edit, MultiEdit e Bash com caminho literal | `test_fixtures_da_raiz_do_forge` (19 fixtures que bloqueiam, entre elas `bash-redireciona-githooks`, `bash-cp-devcontainer`, `bash-rm-devcontainer`, `s0/s2/s6`, `multiedit-commit-msg`) | caminho literal; pasta que contém a entrada (`rm -rf`) | passou (rodado local, OK) |
| Erro interno fecha só no Write e no Edit | `errointerno-write-githooks-bloqueia`, `errointerno-write-sem-entrada-libera`, `errointerno-bash-githooks-libera` | Write com e sem a entrada; Bash com a entrada | passou |
| Sai a guarda da grafia do Bash (`destino_opaco`, `checar_texto`, `colada_em_vigor`, `ref_inteira`, `NOMES_EM_VIGOR`, `MOTIVO_EM_VIGOR`) | busca por referências remanescentes; `forge-mutante --cobertura --base origin/develop` | n/a | sem referência viva em código ou teste; só linhas `apagada` |
| Os 22 fixtures de grafia e as specs -4 e -5 saem sem perder cobertura do que fica | diff das fixtures removidas (s1, s3, s4, s5, s7, s8, s10 a s15, variável de for/read, heredoc, substituição, colada por aspas) | n/a | todas eram só grafia (variável, colagem, `python -c`); as de caminho literal ficam |
| Pisos do teste ajustados (29 liberam, 19 bloqueiam) | `test_fixtures_da_raiz_do_forge` | suíte vazia: pisos conferidos | passou |

## Mutantes
```
forge-mutante: pedido=v0481-hook-raiz-forge rev=27641d2acf10 spec=e348cea8… spec=7f83cbea… spec=0656b6fb…
RF1 RF2 RF3 RF4 RF7 RF8 · morreu
RE1 RE2 RE3 RE4 RE5 · morreu
RX1 RX2 RX3 · morreu
```
14 de 14 mortos, sem sobrevivente. Cobertura (`--cobertura --base origin/develop`): só linhas `apagada`; a condição nova (`not entrada.get("command")`) tem RX2 e RX3.

## Limites
- A proteção do ambiente (sandbox do SO, S21 a S25) não é reproduzível pelo QA aqui; o parecer vale para o hook e depende da evidência da segurança (E37.25).
- Sem teste novo de regra: o vermelho antes do verde não se aplica; a mudança remove guarda e ajusta fixtures.
