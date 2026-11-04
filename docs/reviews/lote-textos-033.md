---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-textos-033
commit: 0349217471b8d9ccd4be4f1e3d11a700e055fb57
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: lote de textos L02 da 0.33 (E13, E17, E20)

## Achados

## Parecer
Aprovado. Só texto, 4 commits, um por item mais o fragmento de changelog; nenhum arquivo de código, de teste nem `tests/config.json` tocado (teto M14 não se aplica).

- E13 (`agents/jarvis.md`, passo 5 do prompt-padrão): o "sem push" saiu; o autor envia a branch de trabalho com `git push origin HEAD:refs/heads/<branch>`, sem `-u`, e o PR segue do integrador (`R-FLUXO`). Bate com FLUXO-6 = A. Nenhuma outra frase de `agents/` ou `skills/` manda "sem push" ao autor (grep).
- E17 (`skills/briefs-e-conferencia/SKILL.md`): o texto antigo (nome com o pedido) ganha a pasta literal `$TMPDIR/<papel>-<pedido>/` com exemplo; coerente com a autoconferência que já existia.
- E20 (`skills/contribuir-com-o-forge/SKILL.md`, seção 5): a sessão de projeto não roda a suíte inteira, o CI roda (`R-CUSTO`, `R-CONTRIB`); "três verdes" virou "duas verdes e os testes dos arquivos tocados", sem sobra do comando antigo. Bate com Q6, leitura 2.
- PA-7 (`achados-recorrentes.md`): conferido; nenhuma classe listada se aplica a texto sem teste. Fragmento `changelog.d/lote-textos-033.md` presente.
- Suíte de convenção (`tests.test_forge`, `tests.test_ambiente_git`, `tests.test_testes_tocados`): ver a linha final do relatório; os checks de `forge-check docs` ficam no pre-push.
