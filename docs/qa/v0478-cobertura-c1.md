---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-cobertura-c1
commit: 67ef9dfbfc2d252ed7d82a7bd34269b5801291db
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 cobertura C1 (T1 vira portão no `pr-texto`)

Escopo: diff `4182a6b9...c4ddc61d` (`tests/catraca.py`, `tests/test_catraca.py`, specs de mutantes, `praticas.md`, fragmento). Sem especificação de UX nem contrato de API: a obrigação é a do fragmento (`changelog.d/v0478-cobertura-c1.md`) e `R-QA`. A suíte inteira roda só no CI do PR; aqui, só os testes do arquivo tocado (sem `.verde` local).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Código sem teste e sem `## Sem teste` barra (R-QA, T1) | `T1NoTextoDoPr.test_codigo_sem_teste_e_sem_secao_barra` | seção vazia | passou |
| Seção com cada arquivo e motivo libera | `test_secao_com_o_arquivo_e_o_motivo_passa` | mínimo exato | passou |
| Lista de arquivos resumida (5 + "e mais N") | `test_muitos_arquivos_resumem_a_lista` | 7 arquivos, acima do corte de 5 | passou |
| Motivo curto barra | `test_motivo_curto_barra` | abaixo de 20 caracteres | passou |
| Citação por caminho inteiro (não pedaço de outro, não comentário) | `test_arquivo_nao_citado_ou_so_como_pedaco_de_outro_barra` | `bin/app2`, `x/bin/app`, comentário HTML | passou |
| Teste mudado ou novo libera | `test_teste_mudado_libera_sem_secao` | n/a | passou |
| Só documentação não pede seção | `test_so_documentacao_nao_pede_secao` | sem código | passou |
| Classe T isenta, N e C barram | `test_classe_t_isenta_e_n_barra` | as três classes | passou |
| Git que falha barra (falha fechada) | `test_diff_dos_testes_ilegivel_barra` | `codigo_sem_teste` devolve None | passou |
| Modo `pr-texto` soma o T1 ao texto (rc 1 e 0) | `test_modo_pr_texto_soma_o_t1` | rc e `(T1)` na saída | passou |
| Motivo vale por arquivo da linha; arquivo só citado sem motivo barra (segurança A2, delta) | `test_motivo_vale_por_arquivo` | 2 arquivos na mesma linha, arquivo sem motivo, 1 motivo por arquivo libera | passou |
| Violação aponta `docs/engineering/praticas.md` (review A2, delta) | `test_violacao_aponta_a_regra_nas_praticas` | sufixo da mensagem | passou |

## Execução
- `python3 -I -m unittest discover -s tests -p test_catraca.py -k T1NoTextoDoPr -k TextoDoPr` (com TMPDIR do sandbox): `Ran 14 tests ... OK`.
- Vermelho antes do verde (cópia em `$TMPDIR` com `tests/catraca.py` da base `4182a6b9` e os testes do head): `-k T1NoTextoDoPr` dá `FAILED (failures=2, errors=15)`; os testes novos caem sem a implementação. O `forge-testes --vermelho 4182a6b9 --modulos test_catraca` abriu com `vermelho: base=4182a6b95a12 head=c4ddc61daa61 módulos=test_catraca (restrito por --modulos)` e `revertidos à base: changelog.d/v0478-cobertura-c1.md, docs/engineering/praticas.md, tests/catraca.py`, mas o módulo inteiro estourou o prazo (rc 124, sem veredito); por isso a prova acima é a manual, por classe.
- Mutantes: `bin/forge-mutante tests/mutantes/v0478-cobertura-c1.json tests/mutantes/v0478-cobertura-c1-2.json`: M1 a M11 `morreu`, rc 0. M11 saiu com a nota "(erro) o teste declarado deu erro sob o mutante e passa sem ele": morte por erro, não por asserção; aceita, pois o teste cai com o mutante e passa sem ele.
- Cobertura: `bin/forge-mutante --cobertura --base 4182a6b9...`: toda linha de guarda do diff (1659, 1669, 1672, 1674, 1677, 1679, 1681, 1928) tem mutante declarado; nenhuma `não coberta` nem `só equivalente`.
- Simulação de merge: não feita; o diff é só em `tests/`, docs e fragmento, e o CI do PR a roda.

## Revalidação no head 67ef9dfb (delta desde c4ddc61d, `escopo: incremental`)
- Domínio lido por `forge-check parecer delta`: `catraca.py` (`com_motivo`, `curtos`, `lista`), `test_catraca.py` (2 testes novos), specs de mutantes (M12 a M16; M9 a M11 reajustados), `catraca.yml` (script da base no passo `pr-texto`), modelo do PR, `praticas.md`, fragmento.
- Testes: `python3 -I -m unittest discover -s tests -p test_catraca.py -k T1NoTextoDoPr -k TextoDoPr` (TMPDIR do sandbox): `Ran 16 tests ... OK`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0478-cobertura-c1.json tests/mutantes/v0478-cobertura-c1-2.json` abriu com `pedido=v0478 rev=67ef9dfbfc2d`; M1 a M16 `morreu`, rc 0 (M11 por erro, como antes, aceito).
- Cobertura: `bin/forge-mutante --cobertura --base 4182a6b9...`: toda linha de guarda do diff (inclui 1678, 1681 a 1683, 1695, 1697) `coberta`; nenhuma `não coberta` nem `só equivalente`.
- Não relido: fora do domínio do parecer. O passo do `catraca.yml` só roda no CI do PR.

## Observações (sem bloqueio)
- Custo do passo `pr-texto` (0,41 s para 0,78 s) e a reversão em 2027-02-18 vêm do fragmento; não reproduzidos aqui, são medida do autor.
- O mérito do texto de `## Sem teste` fica com o review (leitura), como diz o `praticas.md`.
