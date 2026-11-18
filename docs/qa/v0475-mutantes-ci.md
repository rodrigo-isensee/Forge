---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-mutantes-ci
commit: c965ed6c98d77ab9c70114f16cecaa73e55262ce
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0475-mutantes-ci (E3.68)

Escopo do diff: só testes e specs (3 specs de mutantes, `tests/test_falhas_no_resumo.py`, `tests/test_forge_tamanho.py`) e um fragmento de changelog; nenhum código de produção mudou. QA independente: a autoria dos mutantes é de outra instância.

## Achados
- A1 (recomendado) tests/mutantes/v0475-mutantes-ci-1.json:1 · isentas obsoletas: dois trechos de scripts/suite-partes.py citam funções removidas e o de falhas-no-resumo.py não cruza condição mudada; `forge-mutante --cobertura --base <Base-sha>` sai rc 2. Limpar as isentas (R-QA).
- A2 (recomendado) changelog.d/v0475-mutantes-ci.md:2 · o fragmento cita tests/test_ci_falhas.py, que não existe; os testes estão em tests/test_falhas_no_resumo.py e tests/test_forge_tamanho.py.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3.68 / R-QA: mutante por condição do leitor de falhas do CI | specs `v0475-mutantes-ci-1..3` (38 mutantes, MC1..MC38) | teto 160/161 do texto, teto da tabela (n e n+1), registro vazio, quadro fora do repo | 38 de 38 morreram |
| Teste por condição nomeada | `test_falhas_no_resumo.py` (43 testes) | separador só de `=`, bloco até o fim do registro, tab como recuo, sem quadro, sem exceção | passou |
| Corpo nulo do PR em `pr_da_branch` (MC38) | `test_forge_tamanho.py::CorpoDoPr` (24 testes no módulo) | `body: None` vira texto vazio | passou |

## Cenários e resultado real
Provas locais, com `TMPDIR` próprio, só os módulos tocados:
- `python3 -I -m unittest discover -s tests -p test_falhas_no_resumo.py`: Ran 43 tests, OK.
- `python3 -I -m unittest discover -s tests -p test_forge_tamanho.py`: Ran 24 tests, OK.
- `bin/forge-mutante --processos 4 <spec-1> <spec-2> <spec-3>`: rc 0, `pedido=v0475-mutantes-ci rev=c965ed6c98d7`, MC1..MC38 todos `morreu`. Em MC7, MC10, MC15, MC16, MC19, MC31 e MC32 o teste declarado morre por erro sob o mutante e passa sem ele (válido: o mutante é detectado).
- Mutante sobrevivente: nenhum. Equivalente declarado: nenhum nos 38.
- Lista contra o diff: o diff não muda linha de guarda de produção, então não há linha sem mutante; as specs cobrem condições já existentes do leitor (condição do #641).
- Vermelho antes do verde: não se aplica ao pedido (só testes sobre código inalterado); a prova de que cada teste distingue é a mutação acima.
- A bateria completa roda no CI do PR (check-run `bateria` do mesmo sha); não repeti a suíte inteira aqui.
- `forge-check docs`: sem erro.

Bugs: nenhum.
