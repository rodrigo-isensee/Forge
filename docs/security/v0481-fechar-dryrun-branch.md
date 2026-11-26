---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-dryrun-branch
commit: 432ac20dda60577b3ff69c649deb5d44a89931fc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.55, #898, volta por delta)

Gatilhos: controle do Forge (bin/forge-fechar, fechamento e merge), guarda com mutante.

Delta lido: `git diff 1bf95225..432ac20d` (bin/forge-fechar, tests/test_fechar.py, tests/mutantes/{mp1311-fechar-cartao,v0478-fechar-lote-2,v0481-fechar-dryrun-branch}.json, docs/fechamento-integrador.md, changelog.d; os pareceres de review e QA não entram). Clone de revisão existente avançado com `--ff-only` até o head remoto 432ac20d.

## Achados anteriores
- A1 (bloqueante, 1bf95225): corrigido. M5 (mp1311) muta `passo 1 ... --ref refs/heads/$ref` (bin/forge-fechar:1679), FL-M11 muta `conferir_1c "$sha_dry"` (:1683); M3 e FL-M12 saíram: a guarda deles (dry-run sem branch mostra o sha não lido; dry-run sem branch não roda o 1c) era do caminho apagado, e a guarda que o substitui, mais estrita, está em M1 a M4 de v0481-fechar-dryrun-branch.json. Âncoras únicas na fonte (`grep -cF` = 1 cada).
- A2 (recomendado, 1bf95225): corrigido. `branch_criada="$sha_dry"` (bin/forge-fechar:1676) arma o `fim()` (:447), que apaga a ref com `git update-ref -d refs/heads/<b> <sha criado>`, também na recusa do 1c; M5 novo (v0481) prova; teste `test_dry_run_sem_a_branch_local_nao_prende_o_passo_real_na_origin_velha` refaz a sonda S2 anterior: o passo real lê o servidor (`--ref <novo>`), sem "envie a branch".

## Aperta, neutro, afrouxa
- **Aperta:** a ref criada pelo `--dry-run` não sobrevive a ele (sucesso, recusa do 1c e `die` depois da criação); o passo real seguinte volta a ler o servidor (FECHAR-CRIA-BRANCH) em vez de uma `origin/<b>` velha. A remoção é por comparação e troca: só apaga se a ref ainda está no sha que o dry-run criou; branch local que já existia não é marcada (`branch_criada` só se define no ramo que cria) e nunca é apagada. `branch_criada` nasce vazia (:123), sem herdar do ambiente.
- **Neutro:** realinhamento de M5 e FL-M11 (mesma guarda, linha nova); saída de M3 e FL-M12 (guarda do caminho apagado, coberta por v0481 M1 a M4); mensagens do cabeçalho e do `registro:` e o texto de docs/fechamento-integrador.md e do changelog; o passo real (:1759, :1844) não mudou.
- **Afrouxa:** nada no delta. Fora do delta (1bf95225), a catraca lê como afrouxamento a remoção de `test_1c_no_dry_run_sem_a_branch_local_nao_roda` e `test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido`; pelo conteúdo, as duas guardas foram substituídas por mais estritas (parecer anterior), mas o portão é do dono: rótulo `afrouxa-regra` ou restauração (R-CONFORMIDADE, R-DECISAO). Vai como cartão ao Jarvis, não como achado deste parecer.

## Provas
- `python3 -m unittest tests.test_fechar tests.test_forge_mutante`: 271 testes OK (1 pulado: shellcheck fora do PATH, o CI roda).
- `bin/forge-mutante` nas três specs tocadas (rc 0; últimas linhas lidas): v0481 M3, M4, M5 (o novo), mp1311 M2, M4, M5 e v0478 FL-M10, FL-M11, FL-M13 morreram.
- CI do head 432ac20d (`gh pr checks 898`, só leitura): suíte 5/5 nas duas versões, passos, verificações longas, instalação e teto de pulados verdes. `bateria (pareceres)` vermelha só pelos pareceres reprovados (R-REVIEW, R-SEGURANCA, R-QA no log); `bateria` vermelha só por agregar `pareceres: failure`; `catraca` vermelha por falha do item (os dois testes removidos acima, R-CONFORMIDADE), não pelo parecer. Sem linha `- ci:` enquanto a catraca não passar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, unittest, `bin/forge-mutante`, `gh pr checks` e `gh run view --log-failed` (só leitura). Faltou shellcheck no PATH (o CI roda).
