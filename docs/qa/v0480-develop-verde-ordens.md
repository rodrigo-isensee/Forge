---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-develop-verde-ordens
commit: 6ce3a41a8ec8219ace8da853b0540eaaea47edd9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA · conserto da develop, guarda das ordens sem leitura de disco (E127.4, PR #814)

Head 6ce3a41a. Sem suíte local: a bateria inteira é o check-run `bateria` do CI do mesmo sha. Aqui, só os testes dos arquivos tocados (`hooks/conformidade.py`, `tests/mutantes/v0480-ordens-guarda.json`) e os mutantes.

Diff contra a base 0e59c446: uma condição em `hooks/conformidade.py` (a entrada `PELA_COPIA_PRINCIPAL` só chama `relativos_a_copia_principal`, que lê o disco, quando o caminho termina na pasta `.forge/ordens/`) e o mutante da guarda ajustado ao texto novo. A decisão não muda: se o destino não cita a pasta, o relativo à cópia principal também não a cita, então a condição nova só corta a leitura do disco.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| ORDENS-SO-JARVIS: recusa a pasta das ordens, também pela cópia principal (`../`, caminho absoluto) | `tests.test_hooks.GuardaDasOrdens` (4 testes) | destino fora da worktree, com a pasta no texto | passa (4 de 4, 3,5 s) |
| Orçamento de CPU do hook com 3000 gravações | `tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` | 3000 heredocs, teto de 3 s intacto | passa, 1,04 s de CPU (limite 3 s) |
| Mutante da guarda casa com o texto novo | `bin/forge-mutante`, spec `v0480-ordens-guarda` | linha de guarda mudada | morreu (abaixo) |

Medida do orçamento, da raiz do repositório, sem `-I`:
- Depois (head 6ce3a41a): `ORCAMENTO-TEMPO ... medido=1.04s limite=3s medida=cpu`; 3000 gravações com 0,55 s a 0,92 s de CPU por forma.
- Antes (base 0e59c446, clone local limpo): `medido=1.14s` e `1.16s` em duas rodadas; 3000 gravações com 0,53 s a 0,97 s de CPU.
- Limite: nesta máquina (12 CPUs, livre) a base também fica abaixo do teto de 3 s, então a falha da develop não se reproduz aqui. A diferença local é de ~0,1 s, dentro do ruído. O ganho de CPU no runner do CI é o que a bateria do mesmo sha confirma; este parecer não o prova sozinho.

Mutantes (`bin/forge-mutante --base 0e59c446`, as duas specs `v0480-ordens-guarda`):
```
base=0e59c44642a8f388649cb794072fd347ebebd8aa mb=0e59c44642a8f388649cb794072fd347ebebd8aa rev=6ce3a41a8ec8219ace8da853b0540eaaea47edd9
fora do diff: M30 · hooks/conformidade.json
forge-mutante: pedido=v0480-ordens-guarda rev=6ce3a41a8ec8 spec=c1dd3416...0d0e spec=627de472...06c8
15 mutantes do delta: todos morreram (nenhum sobrevivente)
```
O mutante da linha mudada (a condição da cópia principal, `hooks/conformidade.py:1612`) morreu pelo teste `test_conformidade_recusa_a_pasta_das_ordens_e_a_copia_principal`. A linha de guarda nova (`em_qualquer_lugar(posix, c)` antes da leitura) é coberta por esse mesmo mutante, que troca a condição inteira. Um mutante que tire só o novo `em_qualquer_lugar` é equivalente em decisão (só corta custo); a prova dele é o teste de orçamento, não um teste de comportamento.

Vermelho antes do verde: o pedido não traz teste novo de regra; o teste de orçamento e o `GuardaDasOrdens` já existiam. Não se aplica `forge-testes --vermelho`.

Estado do CI no momento da leitura: `catraca` falhou e `bateria`/suítes pendentes; a catraca fica para o tech-lead conferir (a falha pode ser a espera dos pareceres do mesmo head). O remoto avançou com os pareceres de review e segurança (62ba9c55), sem mudar código.

Parecer aprovado sobre o head 6ce3a41a, condicionado a que o `bateria` do mesmo sha feche verde (é ele que prova o ganho de CPU no runner).
