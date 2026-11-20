---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae8-ruleset
commit: a298cdbcdccf035d91769e2beb5707e22ec162cd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E58.3, AE8.1 no head a298cdbc)

## Escopo lido
Diff `5ccac0bf..a298cdbc`: `docs/protecao-de-branch.md` (+25), `templates/projeto/docs/engineering/protecao-de-branch.md` (+18) e `changelog.d/v0479-ae8-ruleset.md`. Só texto, 0 linha de código (H1 fora de questão); sem guarda nova, sem mutante a declarar. Suíte não rodada (brief: sem suíte local); `docs/engineering/praticas.md` não tem regra "decidida por", nada a citar de ferramenta.

## Conferência contra o desenho
- Cobre o AE8.1 do desenho (`docs/propostas/v0479-melhorias-anti-erro.md`, seção AE8 (a), texto): achar o ruleset com bypass, tirar o ator, conferir; emergência pelo modo conserto da BP2, nunca por bypass. D10 (o `main-do-dono` mantém "só por PR" e não alcança a `develop`) e o gatilho de reabertura (2 episódios de mais de 4 h) batem com a seção 7 do desenho.
- `R-CONFORMIDADE`: a escrita fica só com o dono, pela interface; a conferência é `gh api` de leitura. Nenhum agente recebe token nem chama API de escrita.
- Referências conferidas na árvore: "Conserto da integração vermelha" (D2) existe em `skills/trabalho-em-paralelo/ritmo-e-corte.md:23`, com as condições que o texto resume; "BP2 I1 e I4" bate com a última linha da mesma seção; AE8.2 existe no corte do desenho (auditoria, `nao-verificavel` para campo ausente), o que o texto repete.
- Medida citada (7 merges fora do fluxo, 2 com a `develop` quebrada; bypass Always no registro do quadro de 15/11 20:51) vem do quadro e do desenho.
- Neutralidade (`R-NEUTRO`): o modelo de projeto fala em "branch de integração" e "portões", sem nome do Forge.
- Changelog em fragmento, sem tocar o `CHANGELOG.md`.

## Achados
- A1 (recomendado) docs/protecao-de-branch.md:43 · "Estado medido em 15/11" junta duas medidas: o bypass Always é do registro de 15/11; os 7 merges (#680 a #715) são posteriores. Separar a data de cada uma evita ler os merges como de 15/11.
- A2 (recomendado) docs/protecao-de-branch.md:58 · A conferência exige `[]` só no `portoes`, mas o quadro (15/11) nomeia o ruleset com bypass como `checks-obrigatorios-develop-main`; citar esse nome no passo 1 e na conferência, para o dono não conferir só o `portoes`.
- A3 (recomendado) templates/projeto/docs/engineering/protecao-de-branch.md:59 · "`conditions.ref_name.include` tem de citar a branch" não cobre alvo por `~DEFAULT_BRANCH` ou `~ALL`, comum quando a integração é a branch padrão do projeto; dizer que esses valores também a alcançam.

## Sondas

## Parecer
Aprovado. O texto cumpre o AE8.1 do desenho, mantém a escrita do ruleset com o dono (`R-CONFORMIDADE`) e a saída da integração vermelha pelo conserto da BP2 (`R-FLUXO`), sem afrouxar portão. Os três achados são de precisão do texto, sem defeito provado: viram cartão depois do merge (`R-REVIEW`).
