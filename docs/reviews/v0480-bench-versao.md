---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0480-bench-versao
commit: 011c4c1e6d6eb550932e0d880b7a89244bb72190
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 E3.6 (PR #870, BENCH-VERSAO, bench real), revalidação por delta

## Escopo lido
Delta lido: `forge-check parecer delta docs/reviews/v0480-bench-versao.md`, intervalo `d2bdd9ab..011c4c1e` (parecer anterior reprovado no `d2bdd9ab`; volta única E3.5 em `d60eb059` e `011c4c1e`). No domínio: `tests/bancada/versao.py`, `tests/test_bancada_versao.py`, `tests/bancada/romanos/pedido.md`, `tests/mutantes/v0480-bench-versao{,-2,-3,-4}.json`, `tests/pesos-d4.json`, `docs/bench-versao.md`, `changelog.d/v0480-bench-versao.md`. Nada fora do delta foi relido. Teto H1: tudo em `tests/` e texto, fora da contagem.

## Conferência dos achados anteriores
- A1 (agente roda o `--executar`): fechado. `SESSAO_DE_AGENTE` (`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`) recusa o `--executar` com saída 2 (`versao.py:407`); a simulação segue permitida. Teste `test_executar_numa_sessao_de_agente_recusa_e_a_simulacao_passa`; mutante M16 morto.
- A2 (credenciais pagas): fechado. `AMBIENTE_PROIBIDO` inclui `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL` e `CLAUDE_CODE_USE_{BEDROCK,VERTEX,FOUNDRY}`; o `Popen` recebe `ambiente_da_sessao()` sem elas (`versao.py:236`). Defesa a mais: um `init` com `apiKeySource` diferente de `none` mata a sessão (limite `api-paga`). O teste fixa a lista à parte do roteiro. Há testes por variável, de herança e de `apiKeySource`; mutantes M17, M20 e M24 declarados (M24 morto aqui).
- A3 (teste instável): fechado. A pasta das transcrições usa a regra de todo caractere não alfanumérico (`test_bancada_versao.py:388`).
- A4 (peso): fechado. `test_bancada_versao: 10.6` em `tests/pesos-d4.json`.
- A5 (`ambiente_git`): fechado. `git` com `env=sem_manutencao()` e bare com `remoto_sem_manutencao` no `setUp`.
- A6 (citação de `README.md`): fechado. O critério 5 descreve o README sem o caminho.
- A7 (guardas sem mutante): fechado. M9-M16 cobrem as sete guardas citadas e a nova; M17-M27 cobrem as guardas novas da volta (api paga, reconferência do escondido, kill, repo descartável, `--remoto-url`, sandbox, ambiente, simulação, validação).
- A8 (recomendado, kill de reserva): feito na mesma volta. `encerrar()` manda SIGKILL após `ESPERA_KILL`; `leitor.join` tem prazo; teste `test_sessao_que_ignora_o_sigterm_morre_pelo_kill` e mutante M19.
- Mudanças novas da volta (achados da segurança): `repo_descartavel` exige `--repo` público, vazio e da conta do `gh`; `so_a_tag` nega `<bench>/escondidos` no sandbox e nas permissões (`Read(//...)`, sintaxe de caminho absoluto); a avaliação reconfere o sha256 numa cópia temporária. Lidas; corretas e testadas.

## Ferramentas citadas
- CI do head `011c4c1e` (run 45503525036): suíte 3.12 e 3.14 (5 partes cada), passos, verificações longas, instalação, teto de pulados e catraca verdes. `bateria (pareceres)` e o agregado `bateria` ficam vermelhos só pelos três pareceres reprovados (R-REVIEW, R-QA, R-SEGURANCA), que esta revalidação e as dos outros portões resolvem.
- Teste do item rodado aqui: `python3 -m unittest tests.test_bancada_versao`, 26 OK.
- Mutantes rodados aqui (`bin/forge-mutante --processos 1 --ids M9,M15,M16,M24`): os 4 morreram. O autor declara os 27 mortos no PR.
- Nada foi executado com `--executar` neste review, e a pasta do bench do dono não foi criada.

## Parecer
Aprovado. Os bloqueantes A1 a A7 estão fechados com teste do ramo de falha e mutante, e o A8 entrou na mesma volta. O CI do head só falha pelos pareceres.
