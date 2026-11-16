---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-textos-testes
commit: 219c3c50ae76ef60bded7b6337ad6803673485d9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-textos-testes

Intervalo revisado: `origin/develop` (c5c3a449) até `219c3c50` (etapa E1.269 do pedido v047). Arquivos: `skills/briefs-e-conferencia/SKILL.md`, `skills/contribuir-com-o-forge/SKILL.md`, `skills/qa-testing/SKILL.md`, `tests/test_forge.py` (classe `RodarUmModuloComIsolamento`), `changelog.d/v047-textos-testes.md`.

## Gatilhos
Texto de skills que descrevem como rodar testes e um teste estrutural novo que executa subprocesso. Sem hook, workflow, `bin/`, segredo, dependência nem controle de bloqueio (`R-SEGURANCA`, `R-CONFORMIDADE`): nenhum portão é afrouxado.

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendação. O que foi verificado:

- Forma nova `python3 -I -m unittest discover -s tests -p test_x.py` (`skills/qa-testing/SKILL.md:74`, `skills/briefs-e-conferencia/SKILL.md:12`, `skills/contribuir-com-o-forge/SKILL.md:38`): o `-I` tira o diretório corrente e as variáveis do interpretador do caminho de importação, o que reduz a chance de um módulo plantado na árvore ser carregado no lugar da biblioteca padrão. É endurecimento, não afrouxamento. O `nice -n 19` e "um arquivo por vez" na contribuição só limitam consumo de recurso local; não mudam o que é testado nem o portão do CI (`R-CUSTO`, `R-REVIEW`).
- `tests/test_forge.py:7485-7525`: o subprocesso roda só comandos que casaram com a regex fechada `FORMA` (literal, sem curinga de conteúdo) ou o literal do terceiro teste; `argv` por lista, sem shell; ambiente reduzido a `PATH`; diretório temporário descartável; `timeout=60`. Quem controla a entrada é o próprio repositório revisado: sem caminho de ataque.
- Textos removidos: a justificativa "(o estado git compartilhado já corrompeu um repositório)" e o exemplo de clone sem refs remotas em `qa-testing` saem, mas as regras ficam (nunca usar worktree de outro clone; conferir `git rev-parse refs/remotes/origin/<base>` antes de confiar). O aviso de que `forge-check docs` e o pre-push barram achado longo sai da skill, mas a checagem segue nas ferramentas. Sem invariante de `tests/config.json` atingida (`RegrasInviolaveis`, `Invariante` e `Neutralidade` OK).
- Diff sem credencial, rede nem caminho pessoal.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: fica com o CI do PR (sem PR nem execução de CI neste head ainda; `R-REVIEW`). Rodei na worktree, sob `nice` e com `-I`: `RodarUmModuloComIsolamento` (3 testes, OK) e `RegrasInviolaveis`, `Invariante` e `Neutralidade` de `test_forge.py` (9 testes, OK). Ferramentas de varredura de segredos e SAST não estão no PATH deste ambiente (lacuna registrada; o diff foi lido inteiro).
