---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-ajudante
commit: e05f8faab1b446658ee262461a6483829eae5c7b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.29, #891, volta única E14.23; classe C)

Revalidação por delta. Já lido: `220ba3fa..ab293a4e` (rodada anterior, no git em `c2f91788`). Lido agora: `ab293a4e..e05f8faa` inteiro (`tests/catraca.py`, `tests/test_catraca.py`, `tests/mutantes/v0481-catraca-ajudante.json` e `-3.json`, `tests/mutantes/v0480-d3-teste-enfraquecido-{2,3,4,9}.json`, `changelog.d/v0481-catraca-ajudante.md`; os pareceres de review e QA só como contexto).

Gatilhos: controle do Forge (a catraca, que decide o bloqueio por teste afrouxado; R-CONFORMIDADE).

## Achados anteriores
- A1 (recomendado, custo da expansão sem orçamento): **resolvido**. `TETO_DAS_EXPANSOES` (`tests/catraca.py:686`) e `_gasta` (`:718-721`) cobram os nós lidos e as chaves somadas num orçamento único do módulo (`:761`), com teste de tempo sobre a entrada da S9 (`tests/test_catraca.py:881-892`) e mutantes CA14 e CA15 mortos. Sonda S13: o leque que levava 100 s fica em 3,1 s (787 KB, duas passagens); abaixo do teto, o pior que medi foi 0,5 s por passagem (49 KB). O custo por módulo agora é limitado; muitos módulos somam linearmente, e queimar os 10 min do job pediria ~1200 módulos de 50 KB num PR visível: disponibilidade só, falha fechada.

## Conferência do delta
- **Desvio do brief (estourado, conta só as diretas em vez de ilegível): aceito, aperta em relação à correção que sugeri.** Ilegível no lado da base tira o módulo de `_testes_por_modulo` e solta todos os testes dele (nada para comparar); contar só as diretas mantém o piso da catraca da base. No lado do head, as duas opções barram. Sondas (catraca da base `220ba3fa`, a do `ab293a4e` e a do head; `sonda.py` e `sonda2.py` no rascunho local `sec891b`):
  - S12 base abaixo do teto, head acima: o head barra "perdeu asserção (estava no ajudante h0)" + valor trocado; a base e o `ab293a4e` não barram (este conta 10^14 asserções no leque). Falha fechada, como o autor afirma.
  - S10 os dois lados acima do teto, asserção do ajudante `h0` tirada: o head passa calado; o `ab293a4e` barra; a base também passa calada. Igual à base: neutro em relação à `develop`.
  - S11 base acima do teto, head abaixo (o PR desfaz o leque) e tira a asserção direta `assert z` de um teste que já chama `h0` com asserção: o head passa calado; a base e o `ab293a4e` barram. É a ressalva S5 da rodada anterior (asserção direta trocada por ajudante com asserção), que já passava sem teto (S5 de referência, repetida: base barra, `ab293a4e` e head passam), e o mesmo efeito se obtém trocando-a por uma asserção direta fraca e não vácua (S6). Pede ainda um módulo acima do teto já mesclado na `develop`, que só entra por PR revisado. Quem escreve o teste não ganha capacidade nova: neutro, sem achado. O piso da contagem só direta, sugerido na rodada anterior, fecharia S5 e S11 juntos; continua opcional.
- **Só aperta ou neutro, por escrito: neutro.** Na árvore real (S14, 6831 testes), os perfis do `ab293a4e` e do head são idênticos módulo a módulo (nenhum estoura o teto), e o tempo fica em 1,44 s → 1,48 s. A mensagem "perdeu asserção (estava no ajudante X)" só acrescenta texto ao motivo (`tests/catraca.py:786-787`); o bloqueio é o mesmo. `fundo` e `teto` novos em `testes_da_arvore` só são passados pelo teste e pelo próprio recuo (`:775`); a chamada de produção (`:810`) usa os padrões. O recuo roda com `fundo=0` e teto infinito, sem expansão: linear.
- **Mutantes realinhados (D3B5, D3C5, D3D2, D3H7, CA6, CA7):** mesma guarda na fonte nova; os quatro D3 e CA1 a CA21 morrem no head (`bin/forge-mutante`, rev `e05f8faab1b4`).
- Testes: `python3 -m unittest tests.test_catraca.AssercaoNoAjudante` → 7 testes, OK. A suíte inteira roda no CI do PR #891 no mesmo head `e05f8faa`: as 10 partes da suíte verdes; Catraca vermelha só pelo rótulo do dono (mudança em `tests/catraca.py`, o controle esperado) e `bateria (pareceres)` vermelha porque os pareceres ainda estavam no `ab293a4e`. O merge depende delas verdes.

Sondas executadas, nenhuma prova bloqueante: S10, S11, S12, S5 (referência), S13 (tempo), S14 (árvore real), acima.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, o módulo de teste tocado, `bin/forge-mutante` e as sondas locais acima (nada externo). Varredor de segredos, SAST e auditor de dependências não se aplicam ao delta, que não traz dependência nem segredo.
