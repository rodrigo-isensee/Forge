---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0474-texto-dir34-h1
commit: 593ff0351231f2d77f211fba7bff2b05b41f5636
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474-texto-dir34-h1

Gatilhos: tests/config.json (invariantes novas e um motivo reescrito), texto do Jarvis e do tech-lead (diretriz 34, H1 no lugar do M14), modelo de projeto (CLAUDE.md e modelo de PR).

## Achados
- A1 (recomendado) skills/falar-com-o-dono/nao-trava.md:10 · o comando exato do bloqueio de ambiente não diz que é só para o dono rodar e que o time não o roda nem contorna o bloqueio; citar R-CONFORMIDADE e R-VERIFY na frase fecha a leitura de que o Jarvis pode desligar a proteção por conta própria.

## Sondas

## Detalhe
- Base 01b4e8ae (merge-base com a origin/develop), head 593ff035; 13 arquivos, só texto, JSON e testes; nada em `hooks/`, `bin/`, `.github/`, `.githooks/` nem permissão.
- Invariantes de `tests/config.json`: comparação por script entre base e head das seções `invariantes`, `invariantes_motivo` e `invariantes_motivo_trecho`. Nenhum arquivo, trecho ou chave saiu; todo trecho da base ainda casa no arquivo do head. Única mudança fora de acréscimo: o `porque` de `**Ritmo diário:**` em `templates/projeto/CLAUDE.md` troca "um PR por dia para a main" por "a versão para a main", com a mesma regra (R-FLUXO); segue a diretriz 34, e o texto novo ganhou invariante própria com motivo.
- H1 no lugar do M14 (`agents/tech-lead.md:21`, `skills/engineering-practices/SKILL.md`, `tamanho-por-item.md`): bate com a DECISÃO DO DONO de 2026-11-17 11:15 no pedido v0474 (150 linhas de código, testes e documentação fora, exceção só com a suíte vermelha e o motivo no PR). O controle aperta: "Não é trava por volume" sai e o teste passa a exigir a sua ausência (`tests/test_forge.py`, `TetoPorPr`); a asserção de que o teto não vira `bloqueante` por volume continua. Informativo: `tests/config.json` deixa de contar no teto (`tamanho-por-item.md:12`); é o que a decisão manda ("testes não contam") e a remoção de invariante segue presa ao teste `RegrasInviolaveis` e ao destaque no título do PR, não ao tamanho. Sem caminho de ataque.
- Diretriz 34: "não trava" e "versão até 2 por dia, ou mais se couber" estão no Jarvis, no tech-lead (`agents/tech-lead.md:43`), em `ritmo-e-corte.md` e no modelo de projeto. R-MAIN fica: `ritmo-e-corte.md:24` (PR `homolog` → `main` mesclado pelo dono), `agents/tech-lead.md:43` (quem mescla na main é o usuário), `agents/jarvis.md:15` e `:40` intactos. As medidas antes da release (placar de mutação, bench, `forge-check decisoes --sem-cartao`) mudaram do tech-lead para `ritmo-e-corte.md:26`, apontado no tech-lead; não eram invariante e seguem como medida, não portão.
- A1: sem caminho de ataque direto (o dono revê o comando antes de rodar e R-CONFORMIDADE vale pelo `Limites` do Jarvis); por isso fica como recomendado. Dono: tech-lead. Esforço P.
- Prova: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.TetoPorPr tests.test_forge.Neutralidade tests.test_forge.DiretrizesDoDonoNaRWip tests.test_jarvis_nucleo` verde no head 593ff035 (55 testes). A suíte inteira roda no CI do PR de integração (`docs/fechamento-integrador.md`); a branch ainda não tem PR nem execução de CI.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varredura de segredos não aplicável (só texto e JSON, sem credencial); a ferramenta de segredos não está no PATH, lacuna registrada.
