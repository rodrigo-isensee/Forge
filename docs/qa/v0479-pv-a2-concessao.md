---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a2-concessao
commit: 9b6dca25db319a73277a5bc2bfaf151af8cd53a6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-pv-a2-concessao (E57.68)

Revalidação única no head 9b6dca25 sobre o parecer reprovado 32c201ec (A1 ressalva e A2 renomeação). Delta lido por `forge-check parecer delta` (intervalo 4c325c55..9b6dca25: `bin/forge_autorizacao.py`, `tests/test_autorizacao.py`, 4 specs de mutantes, changelog). Suíte inteira fica no CI do PR (check-run `bateria` do mesmo sha, não rodado aqui).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem ressalva: vocabulário fechado, sem marca de negação ou condição (item 5, A1 anterior) | test_alvo_sem_marcador_fora_da_frase_ou_com_ressalva_nao_nasce_ativa | "depois do CI", "antes da release", "sem a segurança", "só com o QA" | passou |
| Data e hora na validade aceitas; termo do ato dentro do nome do cartão não vale | test_vocabulario_fechado_sem_marca_aceita_data_e_hora_e_o_termo_do_ato_fora_do_nome_do_cartao | `18h`, `18/11`, `12:00`; cartão vizinho | passou |
| Depois do Commit só pareceres do próprio Ramo, renomeação conta (A2 anterior) | test_so_o_parecer_de_review_ou_codigo_renomeado_para_a_pasta_de_parecer_fica_inativa | `git mv codigo.txt docs/qa/codigo.txt`; faltar review, qa ou segurança | passou |
| Demais (head exato, ref origin, GIT_*, forma do Commit/Ramo) | 5 testes de ItemPresoAoCommit | sha curto, ramo `-x`/`a..b` | passaram |

## Cenários e resultado real
Vermelho (`R-QA`), `timeout 900 bin/forge-testes --vermelho d4f0b10a --modulos test_autorizacao`, rc=0:
```
vermelho: base=d4f0b10aead7 head=9b6dca25db31 módulos=test_autorizacao (restrito por --modulos)
ItemPresoAoCommit.* (8 testes): 7 prova (asserção), 1 prova (API ausente: fora_do_vocabulario)
Ler.* (8 testes): H=ok B=ok · não prova (passa na base)
contagem: não prova (passa na base)=8; prova (API ausente)=1; prova (asserção)=7
```
Mutantes (4 specs, `--processos 2`, `timeout 900`): rc=0, M1 a M32 todos `morreu` (32 linhas), sem sobrevivente nem sem veredito.
Cobertura (`--cobertura --base d4f0b10a`): rc=0; zero `não coberto`, zero `isenta velha`.

Sondas do QA refeitas, estado do head:
- A1: `fora_do_vocabulario` devolve palavras barradas para "depois do CI verde", "antes da release", "sem a segurança", "só com o QA", "quando o CI passar", "mas só até sexta"; devolve [] para "hoje 18h" e "até 18/11". Corrigido.
- A2, repositório git real: base com 3 pareceres aprovados = ""; `git mv codigo.txt docs/qa/codigo.txt` = "Commit não é o head"; parecer de segurança removido = "sem os pareceres aprovados"; parecer de outra branch adicionado depois = "não é o head"; renomear parecer dentro de docs/qa = "" (legítimo). Corrigido.

Bugs: nenhum aberto (A1 e A2 do parecer anterior fechados). Residual sem bloqueio: o vocabulário é lista fechada, então frase legítima com palavra nova (ex.: "depois") vira `adulterada` e o dono reescreve; é o comportamento pedido pelo item 5.
