---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: d50b9cd0783da93d77709cdba273c1f45ce053b2
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (E6.1, lote de devops)

## Achados
- A1 (bloqueante) tests/test_ferramentas_portoes.py:60 · a conferência do sha256 (preparar-estacao.sh:85) não tem teste que a prenda: trocada por `true`, os 6 testes passam. test_soma_errada roda sem ARQ, a soma sai vazia e cai na mesma mensagem. Passe ARQ e soma errada (R-QA).
- A2 (recomendado) tests/test_ferramentas_portoes.py:75 · test_modo_container_nao_baixa_ferramenta passa na base (vermelho: não prova); só guarda o texto do preparar_container, aceitável como regressão.

## Critério → teste → resultado
Sem especificação de UX (pedido de ferramenta); a obrigação vem do escopo E6.1 e do comentário PORTAO-DEVOPS-FERRAMENTAS.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Binário só entra com sha256 batendo | test_soma_certa_instala_o_binario, test_soma_errada_nao_instala | soma errada | falhou: o ramo "soma errada" não é exercido (A1) |
| Já instalada não baixa | test_ja_instalada_nao_baixa | ferramenta presente | passou |
| --simular não grava | test_simular_lista_as_tres_ferramentas_de_binario_e_nada_e_gravado | nada gravado | passou |
| Falta de pipx vira `falta:` | test_sem_pipx_zizmor_e_semgrep_viram_falta | sem pipx | passou |
| --container não baixa binário | test_modo_container_nao_baixa_ferramenta | n/a | passou (não prova na base) |
| Ensaio só em alvo descartável (texto) | leitura de skills/ci-cd e cyber-security | n/a | texto presente; sem hook, como o escopo manda |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_ferramentas_portoes.py` (TMPDIR do sandbox): 6 testes, OK. `bash -n` do script: ok. shellcheck ausente na estação, não rodado (CI cobre).
- Vermelho antes do verde: `bin/forge-testes --vermelho 4182a6b9 --modulos test_ferramentas_portoes`, saída: `vermelho: base=4182a6b95a12 head=d50b9cd0783d`, 5 "prova (asserção)", 1 "não prova (passa na base)" (container), rc 0.
- Mutação à mão (QA), numa cópia de `git archive HEAD`: trocar `[ "$(sha256sum ...)" = "$esperado" ]` por `true` em preparar-estacao.sh:85. Resultado: SOBREVIVEU (6 testes OK). Causa: o curl falso grava as somas com o nome `x`, o awk não acha o arquivo, `esperado` fica vazio e o teste "soma errada" passa pelo ramo de soma ausente, não pelo de soma divergente. Correção: o agente de devops/dev põe ARQ no teste de soma errada.
- Suíte inteira: não rodada localmente; vale o check-run `bateria` do CI do mesmo sha.
