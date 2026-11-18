---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-brief-gerar
commit: 2008e612de013e287fe544cd1f04dd4332a899f9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0476-brief-gerar (E3.94, cobre E3.48)

## Critério → teste → resultado
| Critério (E3.48) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fora do escopo só pelos ids, 40 por linha; pedido de 600 etapas abaixo de 10.000 caracteres | `test_brief_tamanho.test_pedido_de_600_etapas_fica_abaixo_do_teto` (etapas codigo e review) | máximo (600 etapas, teto do brief, 15 linhas de ids) | passou |
| `forge-check proximo` com `--etapa` do Cobre | `test_brief_tamanho.test_proximo_so_da_etapa_do_cobre` | n/a | passou |
| Brief de portão traz o formato dos Achados; o do autor não | `test_brief_tamanho.test_portao_traz_o_formato_dos_achados_e_o_autor_nao` | permissão do papel (portão x autor) | passou |
| Linhas curtas do erro recorrente e das PQs do autor | `test_erros_no_brief` (49), `test_etapa_do_brief` (89), `test_brief_gerar_custo` (3) | n/a | passou |

## Provas
- Testes dos arquivos tocados (`python3 -I -m unittest discover -s tests -p test_<m>.py`, TMPDIR próprio): brief_tamanho 3 OK; brief_gerar_custo 3 OK; erros_no_brief 49 OK; etapa_do_brief 89 OK; forge_tamanho 24 OK; testes_tocados 162 OK (1 skip já existente no módulo, não adicionado aqui).
- Vermelho antes do verde: `forge-testes --vermelho` foi barrado pelo hook R-TETO (tarefa pesada de outra sessão). Feito à mão, como a skill permite: base 5fb2c856 extraída em cópia no TMPDIR, `test_brief_tamanho.py` novo copiado: `FAILED (failures=3, errors=1)` (os dois subtestes do teto e o do `--etapa` caem; o dos Achados dá erro por `LINHA_DOS_ACHADOS` inexistente). No head, 3 OK.
- Mutação: `bin/forge-mutante tests/mutantes/v0474-e348.json`: M1..M6 morreram, rc=0. `forge-mutante --cobertura --base 5fb2c856`: linhas 8711 e 8734 cobertas; sem condição sem mutante; spec v0457-aqr2 editada (mutantes das linhas apagadas retirados, 8578/8579 apagadas).
- `forge-check docs`: rc=0.
- Suíte inteira: fica no check-run `bateria` do CI do PR (não rodada aqui).

## Achados
