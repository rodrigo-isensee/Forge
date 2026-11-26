---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-status
commit: 0b412b4a210a147c26fb53074f698f6b50b39ab5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E20.5, #910, 1ª rodada completa)

Gatilhos: controle do Forge (bin/forge-check, despacho novo; bin/forge-testes), leitura do gh e de docs/pedidos, saída lida pelo Jarvis.

Lido: `git diff 8ae4d6c6..0b412b4a` inteiro (bin/forge-check, bin/forge_estado.py, bin/forge-testes, tests/test_forge_status_estado.py, tests/mutantes/v0481-s1-status{,-2,-3,-4}.json, tests/pesos-d4.json, changelog.d) e o que o status chama: `gh_json` (bin/forge-check:1518), `sem_controle` (:3627), `versao_da_propria_copia` (:10938), `forge_dono.cmd_abertas` (bin/forge_dono.py:607) e bin/forge-contador.

## Achados
- A1 (bloqueante) bin/forge_estado.py:100 · data de pergunta ao dono fora do calendário (casa o padrão AAAA-MM-DD, ex. 2026-02-30) faz o fromisoformat lançar ValueError fora do NaoVerificavel: traceback, rc 1, sem as linhas 5 e 6; o contrato é não verificável e rc 0. explorável: S1
- A2 (recomendado) bin/forge_estado.py:134 · a limpeza `ctx["seguro"]` da linha impressa não tem teste nem mutante: tirá-la deixa os 19 testes verdes (sonda local); título de commit com U+2028 ou ESC chega cru ao Jarvis. Teste com esses caracteres no título do último merge.

## Sondas
- S1 · p1.md com PERGUNTA AO DONO (2026-13-45 10:00): A ou B?; forge-check status --raiz-pedidos <tmp> --agora 2026-11-26T12:00Z sem gh · espera: decisões não verificável, seis linhas, rc 0 · obtido: ValueError month must be in 1..12 (:100), rc 1

## Detalhe dos achados
**A1.** Evidência: bin/forge_estado.py:100; a hora vem de `_DATA` (bin/forge_dono.py:497, `\d{4}-\d{2}-\d{2}` e `\d{2}:\d{2}`), que aceita mês 13, dia 30 de fevereiro e 25:99; `executar` (:129-133) só apanha NaoVerificavel. Caminho: qualquer pedido do projeto (escrito pelo Jarvis, por agente ou à mão; um erro de digitação basta) derruba o comando inteiro; o Jarvis fica sem a última versão publicada e o plugin da sessão e volta a afirmar estado de memória, que é a trava que o item tira. Severidade: baixa (disponibilidade do controle, sem dado exposto), mas é defeito provado do requisito declarado no docstring (:4-5) e no help. Correção mínima: em `decisoes`, `try: ... fromisoformat(...) except ValueError: raise NaoVerificavel("data ilegível ...")` (ou reaproveitar `instante`), e teste com data fora do calendário; mutante que tira o `except`. Esforço P. Dono: autor do item (E20.1).

**A2.** Evidência: bin/forge_estado.py:134; nenhum teste usa caractere de controle e o contexto falso do teste troca `seguro` por identidade (tests/test_forge_status_estado.py:40). Caminho: o título do último merge na develop (:48) e o stderr do gh (:40) vão para a saída lida pelo modelo; um título com U+2028 imitaria a linha `status: decisões do dono abertas: 0`. Hoje a limpeza existe e funciona; o risco é regressão silenciosa (quem escreve na develop já é mantenedor, por isso recomendado). Correção mínima: teste de ponta a ponta (ou com `seguro=sem_controle`) com U+2028 e ESC no título e mutante que tira o `ctx["seguro"]`. Esforço P. Dono: autor do item.

## Aperta, neutro, afrouxa
- **Aperta:** o Jarvis passa a ter o estado lido na hora (S1a). Só leitura conferida: `gh api` sem `-X`/`-f` (GET), `gh pr list`, `gh release view`, todos com teto de 10 s e stdin fechado; o forge-contador roda com `-I`, teto de 20 s e stdin fechado e só chama `git tag`/leitura, sem fetch nem escrita; `cmd_abertas` recusa docs/pedidos por link simbólico e lê com teto. Nenhuma escrita em disco no módulo. Títulos de PR de terceiros não são impressos (só números). Toda linha passa por `sem_controle`. Os testes usam gh falso (tests/gh_falso.py e `gh_json` falso), PATH sem o gh real e HOME temporário: sem rede.
- **Neutro:** o subparser e o despacho em bin/forge-check (:11198, :11543) só acrescentam o comando; MAPA e lista FORGE_CHECK em bin/forge-testes; peso em tests/pesos-d4.json; changelog.
- **Afrouxa:** nada. Nenhuma guarda existente foi mexida; a catraca pede o rótulo `afrouxa-regra` só por tocar bin/forge-check (decisão do dono, R-CONFORMIDADE, R-DECISAO).

## Provas
- `python3 -m unittest tests.test_forge_status_estado`: 19 testes OK.
- `bin/forge-mutante` nas quatro specs (rc 0): 32 de 32 morreram.
- CI do head 0b412b4a (`gh pr checks 910`, só leitura, com a suíte ainda rodando): `suíte (3.12 e 3.14, parte 3/5)` vermelha por defeito do item: test_indice_forge, docs/indice-forge.md desatualizado sem a linha de bin/forge_estado.py (rode scripts/indice-forge.py); `catraca` vermelha por bin/forge-check sem o rótulo do dono (R-CONFORMIDADE); `bateria (pareceres)` vermelha pela falta dos pareceres (R-REVIEW). Sem linha `- ci:`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, unittest, `bin/forge-mutante`, `gh pr checks` e logs dos jobs pela API (só leitura). gitleaks e zizmor não se aplicam ao diff (sem segredo nem workflow).
