### Alterado
- F6, corte do envio (E32.9): o push na develop não repete a suíte que o PR já rodou (job arvore-envio, scripts/arvore-testada.py --do-pr); a prova liga o job bateria ao run do ci.yml do PR (mesmo número, base develop, base do run ancestral do head, tentativa mais recente), corrigindo o A1 da segurança do #929 (v0481 E32.9).
