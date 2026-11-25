---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 1d6692f507ac6bf65faf1b5be6cff0de3403c9dc
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 prazo-forge (#888, classe C), delta 21a96c1a..1d6692f5 (E7.38)

Escopo: `git diff 21a96c1a..1d6692f5` lido: `PRAZO_DO_MERGE_S` de 8 para 7,5 em `hooks/_comum.py:2826` (A5 da segurança, opção (a)), teste novo `SondaS1ComRelogioFalso.test_recusa_do_prazo_longo_presa_deixa_folga` com `FOLGA_DE_PAREDE_S = 1.5`, a S1 do prazo longo derivada da constante, 3 fixtures de merge com git lento de 4 para 3,5 s, fixture de 9 s com a mensagem "7.5 s", spec P1 de `v0455-prazo.json`, M13 em `v0481-prazo-forge-2.json`, tabela de `prova_de_carga.py`, changelog. Parecer anterior (21a96c1a, aprovado) lido. Clone: `/root/.forge-contrib/wt/v0481-prazo-forge-qa`, no head do remoto (`git ls-remote` = 1d6692f5).

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A5 (E7.32): prazo longo + sessão + registro presos saem com 1,5 s de folga antes do `timeout` do hooks.json | `test_recusa_do_prazo_longo_presa_deixa_folga` | soma dos vigias (8,5 s) <= timeout 10 menos folga | passou; M13 (7,5 para 8,0) morre |
| S1 do prazo longo: recusa na fronteira, libera dentro, derivada da constante | `test_s1_recusa_no_prazo_longo_libera_dentro_e_recusa_na_fronteira` | prazo exato, 0,01 s e 0,4 s abaixo | passou |
| S1 real recusa o git de 15,5 s (sem passar por carga) | `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` | git acima do prazo | cabe ao CI (suíte inteira) |
| Merge com git lento de 3,5 s libera; de 9 s recusa em 7,5 s | `test_prazo_do_merge` | prazo longo vs 3 s | ver "Carga" abaixo |

## Cenários e resultado real
- Rodado só o item: `python3 -m unittest tests.test_hooks.SondaS1ComRelogioFalso tests.test_hooks.PrazoVencidoNaSessaoDoForge tests.test_hooks_volta_propriedades.VigiaAgentesPesado`: `Ran 12 tests in 32.304s OK`. Suíte inteira: só no CI do PR; não cito `.verde` local.
- Vermelho antes do verde: o M13 é o vermelho do teste novo (com `PRAZO_DO_MERGE_S = 8.0` ele cai, morreu).
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-prazo-forge.json tests/mutantes/v0481-prazo-forge-2.json --processos 2`, cabeçalho `rev=1d6692f507ac`: M1 a M13 `morreu` (M4 e M9 por erro do teste declarado, que passa sem o mutante; `M13 · morreu · hooks/_comum.py:2827`). Nenhum sobrevivente. A guarda mudada do diff (uma linha, 2826) tem mutante (M13).
- **A5 fecha.** Sonda em arquivo, hook `parecer.py` real (`python3 -s -E`, corte de 10 s), comando `gh pr merge` por branch com `--squash`, FIFO no `commondir` da worktree, 48 laços de CPU sobre a máquina já carregada (load 58 a 60). Sessão do Forge: 7 de 7 com rc 2, em 8,67 a 9,31 s. Projeto: 5 de 5 com rc 2 (erro interno do parecer, que recusa), em 7,3 a 9,0 s. Nenhuma das 12 rodadas passou do corte (0 liberou). Sem os laços extras, Forge 7 de 7 rc 2 em 8,2 a 8,5 s. Na medição da segurança, o head com 8 s liberou 1 de 7 sob carga parecida.
- **Nada que barra hoje deixa de barrar:** a mudança só encurta o prazo (8 para 7,5 s); o que vencia antes continua vencendo (recusa), e a margem de decisão dos fixtures de merge é a mesma (7,5 menos 3,5 = 8 menos 4 = 4 s). O prazo menor só pode recusar mais, nunca liberar.
- **Carga (falhas que o autor relatou em `Hooks.test_prazo_do_merge`):** reproduzidas aqui, e só sob carga. Com a máquina a 58 a 140 de load, 2 a 3 dos 3 fixtures de merge que liberam recusam com "não decidiu em 7.5 s" (o hook gasta mais de 4 s de relógio fora do `sleep` do git). É a classe DEFEITO-TESTES-DE-PRAZO-SOB-CARGA, com a margem de 4 s inalterada pelo diff; não é regressão do delta. Quem decide é o CI.
- `forge-mutante tests/mutantes/v0455-prazo.json`: os controles de P1 a P6 e P9 a P13 saem `controle vermelho` aqui pelo mesmo motivo (o teste de controle `test_prazo_do_merge` cai sob carga); P7 e P8 morrem. É sem veredito neste sandbox, não sobrevivente; o P1 realinhado (`7.5` para `3.0`) é coerente com a constante.
- Sem acessibilidade nem E2E (hook de linha de comando).

## CI do PR
O head `1d6692f5` não tinha nenhuma execução do CI no PR #888 na hora da leitura (as últimas, do head `f17ee6f4`, com a suíte 3.12 e 3.14 das 5 partes verdes e `bateria (pareceres)` vermelha por falta de pareceres). Sem run no head, não gravo a linha `- ci:`. Quem mescla confere no check-run do sha final que as partes de `test_hooks` (fixtures de merge e `mesma-sessao-libera`) ficam verdes; vermelhas, bloqueiam.
