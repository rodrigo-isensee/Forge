---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-sem-auto
commit: f5143cea54012131715eeac79681695e39c23d5e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-fechar-sem-auto (FECHAR-NUNCA-AUTO, PR #855)

## Critério → teste → resultado
Obrigações (decisão do dono de 24/11, E171.1): nenhum `gh pr merge` com `--auto`; o passo 6 exige todo check-run do head verde; cópia velha do `bin/forge-fechar` se recusa.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem `--auto` em `bin/` e `scripts/` | `SemAutoNaFonte` (3 testes; o detector é provado contra o passo 6 antigo e a continuação `\`) | pasta renomeada (mínimo de 20 arquivos e 1 merge) | passou |
| Check-run extra terminado fora de success para | `test_check_run_fora_dos_obrigatorios_terminado_fora_de_success_para` | failure, cancelled, neutral, timed_out, action_required | passou |
| Check-run extra pendente espera e para no prazo | `test_check_run_fora_dos_obrigatorios_pendente_espera_e_para_no_prazo` | prazo `--espera` | passou |
| Skipped e execução antiga vermelha não bloqueiam | `test_skipped_e_execucao_antiga_vermelha_nao_param_e_mescla` | id maior vale; skipped fora | passou |
| Cópia diferente da origin/develop recusa em todos os modos | `test_copia_velha_recusa_em_todos_os_modos_...` | normal, --dry-run, --limpar, --lote, --promover | passou |
| Develop sem o arquivo; busca que falha | `test_develop_sem_o_arquivo_recusa`, `test_busca_que_falha_recusa_mesmo_com_a_local_igual` | ref local igual e servidor inacessível | passou |
| Confere contra o servidor, não a ref local | `test_confere_contra_a_develop_do_servidor_nao_a_local`, `test_copia_igual_a_da_develop_segue` | ref local velha ou adiantada | passou |
| Dispensa só com TESTE e COPIA_LIVRE juntos | `test_copia_livre_sem_o_modo_de_teste_nao_dispensa` | uma das duas variáveis só | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_fechar_sem_auto.py`: 12 testes, OK (23,6 s).
- Suíte inteira: não rodei; vale o check-run `bateria` do CI do PR no mesmo sha (a conferência do review/CI fica com o portão).
- Sem `skip`, `expectedFailure` nem espera fixa nos testes novos. A variável `FORGE_FECHAR_COPIA_LIVRE` entra no `setUp` de `test_fechar.py` (ajuste mínimo e coerente com o oráculo).
- Merge de `develop` no head (f5143cea) conferido: o diff contra a base não traz `url_normal` removida; o E166.1 segue intacto.

### Vermelho antes do verde
`bin/forge-testes --vermelho c752c227 --modulos test_fechar_sem_auto,test_fechar` (rc 0):
```
vermelho: base=c752c227bb6b head=f5143cea5401 módulos=test_fechar_sem_auto,test_fechar (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/v0480-fechar-sem-auto.md, tests/pesos-d4.json
contagem: não prova (passa na base)=113; prova (asserção)=9; pulado=1
```
Os 9 que provam: 6 de `CopiaDaDevelop` e 3 de `TodoCheckRunDoHead` (H=ok, B=falha). Os 3 de `SemAutoNaFonte` passam na base de propósito: o `--auto` já saíra do script (decisão de 21/11) e eles são a guarda de regressão, com o detector provado contra o texto antigo. O único pulado é `test_shellcheck_fechar_passa_limpo` (sem shellcheck no ambiente; já era assim na base; o CI roda o shellcheck).

### Mutação
`bin/forge-mutante tests/mutantes/v0480-fechar-sem-auto.json tests/mutantes/v0480-fechar-sem-auto-2.json --processos 2` (rev=f5143cea5401):
```
N1 · morreu · bin/forge-fechar:331
N2 · morreu · bin/forge-fechar:331
N3 · morreu · bin/forge-fechar:333
N4 · morreu · bin/forge-fechar:334
N5 · morreu · bin/forge-fechar:336
N6 · morreu · bin/forge-fechar:337
N7 · morreu · bin/forge-fechar:955
N8 · morreu · bin/forge-fechar:956
N9 · morreu · bin/forge-fechar:958
N10 · morreu · bin/forge-fechar:958
```
Nenhum sobrevivente. Lista conferida contra o diff: uma guarda por linha mudada (dispensa dupla, busca, arquivo ausente, blob, chamada, terminado, pendente, skipped, id mais recente). `forge-mutante --cobertura --base c752c227` sai `não coberto: bin/forge-fechar` (shell, a ferramenta só lê Python) e `tests/pesos-d4.json` (dados); a conferência foi manual, acima.

### Estados do check cobertos
Pendente (espera e prazo), falho (cinco conclusões), pulado (ignorado), repetido (a execução mais recente por nome decide), em linha com o pedido.
