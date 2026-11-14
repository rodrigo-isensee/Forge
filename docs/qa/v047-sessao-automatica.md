---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-sessao-automatica
commit: 5f0547cc0864a1830cd32f51f6695b35fc772703
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-sessao-automatica (E1.217)

Intervalo `origin/develop...5f0547cc` (merge-base f4b0c2ae). Classe C: SESSAO-AUTOMATICA (diretriz 28) e GH-VERSAO-MINIMA. Sem especificação de UX nem contrato de API: as obrigações vêm do cartão E1.198 do pedido v047 (`docs/pedidos/v047.md`), numeradas aqui como CA-1 a CA-4. A suíte inteira roda no CI do PR (ainda sem PR); aqui rodei só os cenários da entrega.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 `jarvis` e `jarvis-forge` abrem com `--permission-mode auto` (inclui `--dev` e retomada com `--continue`) | `test_sessao_automatica.AtalhosAbremNoAutomatico` (3 testes de atalho) | retomada (`--continue`) e modo `--dev` | passou; mutantes S1, S2 morreram |
| CA-2 README, modelo de projeto e roteiro do preparar-estacao mandam abrir o `claude` no automático e o Jarvis conferir o sandbox | `test_nenhuma_instrucao_manda_abrir_o_claude_sem_o_modo`, `test_modelo_de_projeto_manda_conferir_o_sandbox` | mínimo de 3 linhas lidas (guarda de suíte vazia) | passou; mutante S3 morreu |
| CA-3 `preparar-estacao.sh` exige gh >= 2.47 e instala pelo repositório oficial; o gh do apt comum sai da lista | `EstacaoExigeGh` (5 testes) | 2.45.0, 2.46.9 (logo abaixo), 2.47.0 (limite), 2.104.0, 3.1.0, saída ilegível | passou; mutantes G1, G2, G3 morreram |
| CA-4 passo 1 do `forge-fechar` para com gh < 2.47 ou ilegível antes de abrir PR, e busca `origin/homolog` se faltar (falha da busca só avisa) | `test_fechar_gh_versao.FecharGhVersao` (10 testes) | 2.46.9, 2.47.0, 1.99.0, 3.0.1, ilegível; sem homolog no servidor | passou; mutantes F1, F2, F3 morreram |

## Cenários e resultado real
- Execução local no head 5f0547cc: `python3 -m unittest tests.test_sessao_automatica tests.test_fechar_gh_versao` → `Ran 19 tests ... OK`. `tests.test_forge.PrepararEstacao` (testes existentes ajustados com o gh falso) → `Ran 11 tests ... OK`.
- Os ajustes em `tests/test_fechar.py` e `tests/test_forge.py` só acrescentam o `--version` ao gh falso; não afrouxam asserção.
- Mutação (`bin/forge-mutante tests/mutantes/v047-sessao-automatica.json`, 9 mutantes, saída 0, todos mortos):
```
forge-mutante: pedido=v047-sessao-automatica rev=5f0547cc0864 spec=0832336d16ba8926b5417843ba3b58f06ff832618d2516d03b7cbcd9a665182b
S1 · morreu · scripts/jarvis:28
S2 · morreu · scripts/jarvis-forge:217
S3 · morreu · templates/projeto/CLAUDE.md:11
G1 · morreu · scripts/preparar-estacao.sh:57
G2 · morreu · scripts/preparar-estacao.sh:282
G3 · morreu · scripts/preparar-estacao.sh:55
F1 · morreu · bin/forge-fechar:859
F2 · morreu · bin/forge-fechar:858
F3 · morreu · bin/forge-fechar:863
```
- Cobertura da lista (`forge-mutante --cobertura --base f4b0c2ae`): `base=f4b0c2ae... mb=f4b0c2ae... rev=5f0547cc...` e `não coberto: bin/forge-fechar`, `scripts/jarvis`, `scripts/jarvis-forge`, `scripts/preparar-estacao.sh` (a ferramenta só lê Python; shell sai assim). Conferi à mão contra o diff: cada guarda mudada tem mutante (modo auto nos dois atalhos, comparação do menor em preparar-estacao e forge-fechar, ilegível nos dois, busca de homolog, gh fora do apt comum, sandbox no modelo). Sem linha de guarda sem mutante.
- Vermelho antes do verde: `forge-testes --vermelho f4b0c2ae` estourou o prazo (`Terminated`, rc 124 com `timeout 170`; sem veredito, não vale como vermelho). Feito à mão: cópia em `$TMPDIR` do head com `bin/forge-fechar`, `scripts/jarvis`, `scripts/jarvis-forge`, `scripts/preparar-estacao.sh`, `templates/projeto/CLAUDE.md` e `README.md` voltados ao f4b0c2ae, rodando os dois módulos novos: `Ran 19 tests ... FAILED (failures=18)`. Os 18 que caem são os testes de comportamento novo; passam na base só os 3 de "gh recente segue" no forge-fechar (comportamento já existente, esperado).
- Simulação de merge: a `origin/develop` avançou além do merge-base (o diff contra a ponta mostra remoções de outros pedidos); o escopo deste parecer é o diff por merge-base, que não toca os arquivos desses pedidos.
- Acessibilidade e E2E de navegador: n/a (sem interface).

## Bugs
Nenhum aberto.
