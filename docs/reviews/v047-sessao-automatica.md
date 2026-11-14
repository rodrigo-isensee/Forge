---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-sessao-automatica
commit: cd7bd9f833b4f8abec6cb95138889ae51f2fdc8d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (SESSAO-AUTOMATICA e GH-VERSAO-MINIMA, E1.215; revalidação E1.233 no cd7bd9f8)

Intervalo `origin/develop..5f0547cc` (merge-base f4b0c2ae, o Base-sha do brief): um commit, 12 arquivos. Classe C (o passo 1 do `bin/forge-fechar` é código de controle). Instância que não fez a entrega (E1.198).

## Achados
- A1 (recomendado) bin/forge-fechar:862 · linha de guarda mudada (`if ! git rev-parse ... origin/homolog`) sem mutante declarado na spec. O teste já a mata (sonda no Parecer), então a lacuna é só de declaração. Somar um F4 em tests/mutantes/v047-sessao-automatica.json (lista do QA, R-QA).
- A2 (recomendado) scripts/preparar-estacao.sh:80 · o ramo de falha "o gh instalado segue abaixo do mínimo" (apt ok, versão ainda antiga) não tem teste. scripts/ não é código de controle; um caso com o gh falso respondendo 2.45 depois do install o cobriria.
- A3 (recomendado) scripts/preparar-estacao.sh:92 · `if ! tem apt-get` do container_pacotes mudou (antes exigia também curl) e o ramo não tem teste. O comportamento está certo: o curl só é preciso para o gh, e o garantir_gh já o confere.
- A4 (recomendado) tests/test_sessao_automatica.py:1 · são 264 linhas de código e teste contra a orientação de 150 (M14). Os dois cartões vão juntos por decisão do dono (lote da estação, 14/11 14:06). O corpo do PR traz `teto: excedido, 264 linhas, <motivo>`.
- A5 (recomendado) scripts/jarvis:33 · o settings.local.json prevalece sobre o settings.json no Claude Code, mas basta um dos dois com enabled true para calar o aviso: settings.json true e local false fica sem aviso. Ler o local por último e deixá-lo decidir quando trouxer a chave.

## Sondas

## Parecer
**Aprovado.** Nada bloqueia: os achados A1 a A4 são recomendados e não fazem a entrega voltar (`R-REVIEW`).

Checklist (leitura):
1. Escopo: atende à diretriz 28 nos atalhos (`scripts/jarvis` e `scripts/jarvis-forge`, inclusive o `--dev` e a retomada), no README, no modelo `templates/projeto/CLAUDE.md` e no roteiro do `preparar-estacao.sh`. Atende também ao GH-VERSAO-MINIMA: a estação exige o gh 2.47 ou mais, instalado pelo repositório oficial, e o `apt` comum deixa de listar o `gh`; o passo 1 do `forge-fechar` recusa o gh antigo ou com versão ilegível antes de abrir qualquer coisa e busca a `origin/homolog` quando falta. O texto do `agents/jarvis.md` (conferir o sandbox no primeiro comando) fica para depois da folga, como registra o cartão SESSAO-AUTOMATICA no quadro. Não é lacuna desta entrega.
2. Regras: `R-CUSTO` e `R-NEUTRO` sem efeito. A busca da homolog é só leitura e, se falhar, vira aviso; o `forge-check pr` continua decidindo (`R-CONFORMIDADE`). O fragmento `changelog.d/` está presente e o `CHANGELOG.md` não foi tocado.
3. e 4. Legibilidade e erros: a comparação maior.menor é a mesma nos dois scripts e está correta nos limites 2.46.9, 2.47.0 e 1.99/3.x, todos testados. As mensagens de `die` dizem o passo, que nada foi aberto nem mesclado e o comando que resolve. O `hash -r` depois do install evita ler o gh antigo do cache do bash. No `--simular`, nenhum comando que altera o sistema é chamado (o teste confere pelo registro).
5. Segurança: o parecer é do `security-engineer` (E1.216), aqui só citado. A chave e a lista do apt seguem o caminho que já existia.
7. Testes: são comportamentais (scripts reais com `gh`, `sudo`, `curl` e `apt-get` falsos e ambiente limpo). O falso do `gh` em `tests/test_fechar.py` responde a `--version` fora do registro, então a regra "lê a 1ª chamada" não muda. O teste de texto do "claude solto" exige no mínimo 3 ocorrências (item 11).
9. Commit: um commit coerente, no formato Conventional Commits em português.

Ferramentas (só citadas):
- `shellcheck scripts/jarvis scripts/jarvis-forge scripts/preparar-estacao.sh bin/forge-fechar`: sc=0.
- `bin/forge-mutante --cobertura --base f4b0c2ae`: `não coberto` nos 4 arquivos de shell, que é o esperado para shell. A lista é conferida pelo QA (E1.217).
- Testes novos rodados neste review: `python3 -m unittest tests.test_sessao_automatica tests.test_fechar_gh_versao`, 19 testes OK em 168,8 s.
- Suíte inteira: fica com o CI do PR (sem PR ainda). Não foi rerrodada aqui.

Sonda de A1 (não é bloqueante, por isso fica fora de `## Sondas`): o mutante `if ! git rev-parse ...` → `if false` na linha 862, rodado numa cópia do 5f0547cc, derrubou `test_busca_origin_homolog_quando_falta` e `test_sem_homolog_no_servidor_so_avisa` (2 falhas). O mutante morre.

## Revalidação E1.233 (delta 5f0547cc..cd7bd9f8)
Delta lido só por `forge-check parecer delta docs/reviews/v047-sessao-automatica.md` (rc=0). No domínio: `scripts/jarvis`, `tests/mutantes/v047-sessao-automatica.json`, `tests/test_sessao_automatica.py`. Commits de código: 40dbcb30 (aviso no stderr sem sandbox, E1.222) e cd7bd9f8 (uma pasta de projeto por chamada no teste). Instância que não fez a entrega.

- A1 resolvido: F4 declarado para `bin/forge-fechar:862` e morre.
- SANDBOX-AVISO: o aviso é só uma linha no stderr; a sessão segue em `--permission-mode auto` (o teste confere o modo e rc=0). `python3 -I` com o heredoc; settings ausente, quebrado ou com `enabled` não booleano conta como desligado (só `is True` cala o aviso). A precedência entre os dois arquivos fica como A5, recomendado: o aviso é informativo e não muda permissão (o parecer de segurança é do `security-engineer`).
- Guardas novas (`if ! sandbox_ligado`, `is True`, a lista de arquivos): uma por linha em W1 a W4, cada uma com teste de comportamento do ramo (projeto real no tmp, `claude` falso, `ambiente_limpo()`); nenhum lê o texto da fonte.
- Mutantes: `bin/forge-mutante tests/mutantes/v047-sessao-automatica.json --processos 1` no cd7bd9f8: 14 de 14 morreram (S1-S3, G1-G3, F1-F4, W1-W4), 5m0s.
- `shellcheck scripts/jarvis`: sc=0.
- Commits: dois, Conventional Commits em português, coerentes.
- Suíte inteira: fica com o CI do PR; não rerrodada.

Parecer mantido: **aprovado**; nada bloqueia, A2 a A5 são recomendados (`R-REVIEW`).
