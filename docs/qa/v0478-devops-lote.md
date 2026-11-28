---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: f00c3da26d6be9051f14ad0b1cfad212b41998b4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (E6.1, lote de devops)

## Critério → teste → resultado
Sem especificação de UX (pedido de ferramenta); a obrigação vem do escopo E6.1 e do comentário PORTAO-DEVOPS-FERRAMENTAS.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Binário só entra com sha256 batendo | test_soma_certa_instala_o_binario, test_soma_da_release_errada_nao_instala, test_soma_fixada_no_script_errada_nao_instala | soma errada | passou: M1 e M2 morrem (revalidação f9356caf) |
| Já instalada não baixa | test_ja_instalada_nao_baixa | ferramenta presente | passou |
| --simular não grava | test_simular_lista_as_tres_ferramentas_de_binario_e_nada_e_gravado | nada gravado | passou |
| Falta de pipx vira `falta:` | test_sem_pipx_zizmor_e_semgrep_viram_falta | sem pipx | passou |
| --container não baixa binário | test_modo_container_nao_baixa_ferramenta | n/a | passou: com garantir_ferramentas inserido no modo container, o teste cai (executa --container --simular, comportamento) |
| Ensaio só em alvo descartável (texto) | leitura de skills/ci-cd e cyber-security | n/a | texto presente; sem hook, como o escopo manda |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_ferramentas_portoes.py` (TMPDIR do sandbox): 6 testes, OK. `bash -n` do script: ok. shellcheck ausente na estação, não rodado (CI cobre).
- Vermelho antes do verde: `bin/forge-testes --vermelho 4182a6b9 --modulos test_ferramentas_portoes`, saída: `vermelho: base=4182a6b95a12 head=d50b9cd0783d`, 5 "prova (asserção)", 1 "não prova (passa na base)" (container), rc 0.
- Mutação à mão (QA), numa cópia de `git archive HEAD`: trocar `[ "$(sha256sum ...)" = "$esperado" ]` por `true` em preparar-estacao.sh:85. Resultado: SOBREVIVEU (6 testes OK). Causa: o curl falso grava as somas com o nome `x`, o awk não acha o arquivo, `esperado` fica vazio e o teste "soma errada" passa pelo ramo de soma ausente, não pelo de soma divergente. Correção: o agente de devops/dev põe ARQ no teste de soma errada.
- Suíte inteira: não rodada localmente; vale o check-run `bateria` do CI do mesmo sha.

## Revalidação (delta d50b9cd0..f9356caf)
- `python3 -I -m unittest discover -s tests -p test_ferramentas_portoes.py`: 9 testes, OK.
- `bin/forge-mutante tests/mutantes/v0478-devops-lote.json --base d50b9cd0783da93d77709cdba273c1f45ce053b2`: `base=d50b9cd0783da93d77709cdba273c1f45ce053b2 mb=d50b9cd0783da93d77709cdba273c1f45ce053b2 rev=f9356caf6fe937fd9d16d11e11c3d4588e4433e7`; M1 morreu (:90), M2 morreu (:92), M3 morreu (:97), M4 morreu (:112). A1 resolvido: a conferência do sha256 agora é presa.
- A2 resolvido: o teste do modo container roda `--container --simular` com curl falso; mutação à mão (insere `garantir_ferramentas` em preparar_container) derruba o teste.
- Suíte inteira: vale o check-run `bateria` do CI no mesmo sha, não rodado local.

## Revalidação (delta f9356caf..f00c3da2)
- Domínio: só `tests/test_ferramentas_portoes.py` (teste novo `test_falha_do_install_sem_tar_vira_falta_e_nao_grava_instalou`) e `tests/mutantes/v0478-devops-lote.json` (M5, M6); sem mudança de código de produção.
- `python3 -I -m unittest discover -s tests -p test_ferramentas_portoes.py`: 10 testes, OK.
- `bin/forge-mutante tests/mutantes/v0478-devops-lote.json --base f9356caf6fe937fd9d16d11e11c3d4588e4433e7`: `base=f9356caf6fe937fd9d16d11e11c3d4588e4433e7 mb=f9356caf6fe937fd9d16d11e11c3d4588e4433e7 rev=f00c3da26d6be9051f14ad0b1cfad212b41998b4`; M5 morreu (:98), M6 morreu (:99); M1 a M4 também morrem na rodada completa. Nenhum sobrevivente.
- Vermelho: sem código novo de produção no delta; o teste novo guarda comportamento existente e a prova dele é a morte de M5 e M6.
- Suíte inteira: vale o check-run `bateria` do CI no mesmo sha, não rodado local.
