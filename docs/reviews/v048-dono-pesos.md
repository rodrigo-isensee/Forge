---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-dono-pesos
commit: ca3c07bb5c4eebe23e849d0031dd9822c5aed05f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 dono dos pesos (#959, DONO-DA-GERACAO-DOS-TEMPOS, classe C, E6.6)

1ª rodada completa no head ca3c07bb (Base-sha ae194fa9). Exceção de tamanho aceita pelo dono (DECISÃO DO DONO 28/11 11:19, 151 linhas fora a lista de mutantes); não é achado.

- ci: ca3c07bb5c4eebe23e849d0031dd9822c5aed05f pendente na leitura (suíte 1/5 em andamento; 2/5 a 5/5, instalação, bateria (passos) e árvore verdes; catraca vermelha, espera parecer ou rótulo). Parecer reprovado por A1, independente do CI.
- ferramenta: `bin/forge-mutante --base ae194fa9 tests/mutantes/v048-dono-pesos.json`: M1 a M13 morreram; specs v047 (-2, -4, -5): todos morreram; `--cobertura --base ae194fa9`: rc 0, sem condição descoberta.
- testes do diff: `python3 -m unittest tests.test_pesos_do_ci tests.test_ci_rapido_guardas`: 45 OK.

## Achados
- A1 (bloqueante) scripts/pesos-do-ci.py:153 · O caminho do PR mesclado nunca coleta: o `pull_requests` da execução vem vazio na API (S1, S2), então `len(lista) == 1` falha sempre. Ache o PR pelo head_sha (`commits/<sha>/pulls`) e troque o falso de tests/test_pesos_do_ci.py:249, que inventa `[{"number": 7}]`, por um com lista vazia.
- A2 (recomendado) scripts/pesos-do-ci.py:71 · As guardas de fork (`head.repo.full_name`) e de sha (linha 72) não têm mutante declarado; os testes as matam (sonda manual: os dois mutantes morreram), mas o `--cobertura` não vê linha de continuação do `return (...)`. Declare ao corrigir A1.
- A3 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:52 · O `--conferir` aparece como capacidade, não como passo: escreva o comando (`python3 -I scripts/pesos-do-ci.py --repo <dono/repo> --conferir`, rc 0) depois de regerar, para o tech-lead rodá-lo na marca.

## Sondas
- S1 · gh api 'repos/<dono/repo>/actions/workflows/ci.yml/runs?event=pull_request&status=success&per_page=100' com o tamanho de .pull_requests por execução · espera: execuções com 1 PR associado · obtido: 0 em 100 de 100
- S2 · gh api repos/<dono/repo>/actions/runs/46148339685 (run do último head do PR 958, já mesclado na develop) · espera: pull_requests com o PR 958 · obtido: event=pull_request, conclusion=success, pull_requests vazio

## Parecer
Reprovado por A1. O filtro em si está certo e testado: `execucao_de_pr_valida` exige evento `pull_request`, ci.yml, repositório e head_repository iguais ao `--repo`, `completed`/`success`, PR com `merged_at`, base `develop`, head do mesmo repositório e `head.sha` igual ao da execução; `perna_valida` separa a perna do push da do PR. O dono (tech-lead) e a geração na marca estão em ritmo-e-corte.md (A3 só pede o comando do `--conferir`). Os 6 specs da v047 (M16, M17, M37, M39, M50, M61) só ganharam contexto para ficarem únicos e seguem mutando a mesma guarda de antes (`execucao_valida`, `perna_valida`, anotações e pesos atuais); todos morrem.

O defeito: o GitHub não preenche `pull_requests` nas execuções `pull_request` deste repositório (100 de 100 vazias, inclusive a do último sha do PR 958, mesclado), e o código só pede `pulls/N` quando a lista tem exatamente um número. Resultado: a coleta do PR descarta tudo e a geração depois do F6 continua sem tempos, o problema que o item resolveria; o fragmento do changelog promete o que não acontece. Os testes ficam verdes porque o falso dá um campo que a API real não dá (checklist 12). Sugestão: para cada execução válida, `repos/<repo>/commits/<head_sha>/pulls` e aceite só o PR cujo `head.sha` é o da execução, com os filtros atuais; teste com `pull_requests: []`.
