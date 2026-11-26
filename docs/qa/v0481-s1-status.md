---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-status
commit: 0b412b4a210a147c26fb53074f698f6b50b39ab5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 S1a, `forge-check status` (PR #910, E20.4, 1.ª rodada)

## Achados
- A1 (bloqueante) bin/forge_estado.py:100 · `fromisoformat` sem guarda: pergunta ao dono com data inexistente (2026-02-30) derruba o status com ValueError, rc 1, sem as linhas 5 e 6. Contrato: `não verificável`, rc 0. Reproduzido; bug em docs/qa/bugs/. Converter em NaoVerificavel, com mutante e teste do ramo.
- A2 (bloqueante) docs/indice-forge.md:42 · bin/forge_estado.py sem linha no índice: test_indice_forge falha (3 testes, reproduzido local) e a suíte parte 3/5 (3.12 e 3.14) fica vermelha. Rodar scripts/indice-forge.py e commitar.
- A3 (recomendado) bin/forge_estado.py:100 · hora da pergunta sem fuso recebe o fuso de `agora`; sem `--agora` a idade depende do fuso da máquina. Declarar o fuso do registro e converter.

## Critério → teste → resultado
Escopo E20.1/E20.2 sem `CA-n` numerado: cada obrigação do brief vira um teste.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| seis linhas `status:` | Executar.test_sem_rede_... | n/a | passou |
| último merge, idade | Itens.test_ultimo_merge_* | resposta fora da forma, data ilegível | passou |
| PRs por estado | Itens.test_prs_* | lista vazia, número não inteiro | passou |
| contador | Contador.* | falha, silêncio, prazo estourado | passou |
| decisões abertas e idade | Itens.test_decisoes_* | zero, sem data, leitura recusada | passou; data inexistente falha (A1) |
| versão publicada e plugin | Itens.test_ultima_versao, test_plugin_da_sessao | tag vazia, plugin ilegível | passou |
| sem rede: não verificável, rc 0 | Executar, PeloForgeCheck | sem gh, `--agora` sem fuso (rc 2) | passou |
| só leitura, sem rede além de leitura | leitura do código | n/a | passou: só gh api GET, gh pr list, gh release view, git de leitura via forge-contador e cmd_abertas; nada grava, sem fetch; testes com gh falso (pasta_com_gh, gh_json injetado) |
| índice do Forge em dia (CI) | test_indice_forge | arquivo novo em bin/ | falhou (A2) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_status_estado.py`: 19 testes, OK.
- Mutantes (bin/forge-mutante nas 4 specs, --processos 4): `rev=0b412b4a210a`, M1 a M32 todos `morreu`, sem sobrevivente. Só a linha 100 (A1) não tem mutante: é a guarda que falta.
- Vermelho: `bin/forge-testes --vermelho 8ae4d6c63c27aed480d822c66f361f53d8d4594d --modulos test_forge_status_estado`: `vermelho: base=8ae4d6c63c27 head=0b412b4a210a`; contagem: não prova (passa na base)=17; prova (asserção)=2 (os dois de PeloForgeCheck, que rodam o forge-check). Nenhum cai no HEAD. Os 17 unitários passam na base porque o forge_estado.py revertido continua importável na cópia; a prova deles vem da mutação.
- Sonda A1: ValueError, rc 1 (bug em docs/qa/bugs/v0481-s1-status-data-invalida.md).

- ci: 0b412b4a210a147c26fb53074f698f6b50b39ab5 vermelho (suíte parte 3/5 em 3.12 e 3.14: test_indice_forge, A2; parte 1/5 em 3.14 cancelada pelo push do parecer do review; bateria (pareceres) e catraca esperam parecer e rótulo)
