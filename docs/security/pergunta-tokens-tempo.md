---
tipo: revisao-seguranca
contrato: 1
pedido: pergunta-tokens-tempo
branch: melhoria/pergunta-tokens-tempo
commit: df1b1b450f1296c27a50d41fccbe6cbabe499cbe
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: pergunta-tokens-tempo

Escopo: `git diff 82c11c03dfcbe7dfe521c6500ef8c976e49995c5 df1b1b450f1296c27a50d41fccbe6cbabe499cbe`, 5 arquivos (+29 / -7): `skills/modo-iniciante/SKILL.md`, a `R-DECISAO`, `agents/jarvis.md`, `tests/test_clareza.py` e o fragmento `changelog.d/pergunta-tokens-tempo.md`. Ameaças consideradas:
- exigência antiga do formato de pergunta ou da `R-DECISAO` sumir na troca de linhas (afrouxamento silencioso de controle do Forge);
- o novo campo de números virar convite a inventar medição, levando o dono a decidir sobre dado falso;
- a fonte do número pedir ferramenta paga, acesso externo, segredo ou dado de pessoa (`R-CUSTO`);
- a saída "decidam vocês" ou as exceções de custo, acesso, exceção a regra e ato irreversível perderem força.

## Gatilhos
`R-SEGURANCA`: a entrega toca a `R-DECISAO`, `agents/jarvis.md` e uma skill do núcleo, que são controles do Forge.

## Resumo
**Aprovado.** Nada do texto antigo se perdeu; a mudança só acrescenta exigência. Como conferi:
- **Comparação caractere a caractere (`difflib`) entre a base e o HEAD revisado**, nos três arquivos de controle. As únicas remoções:
  - `skills/modo-iniciante/SKILL.md:35` (item 4): "quanto tempo a mais ou a menos por demanda, em faixa e média, ou "não medido"" virou "**tempo** e **tokens** a mais ou a menos por demanda, cada um em faixa e média, marcado `medido`, `estimado` ou `não medido`". Saiu a palavra "quanto" e as aspas viraram crase; o tempo, a faixa, a média, a unidade por demanda e o "não medido" continuam, e "Afrouxa o processo? (sim ou não, por opção)" está intacto.
  - `skills/modo-iniciante/SKILL.md:41-43` (exemplo): o rótulo "Eficiência:" virou "Tempo:" nas três opções, com os mesmos números (0 a 1 h, média 0,5 h; 1 a 3 h, média 2 h; sem diferença); "Afrouxa o processo? Não." e o "sem custo por mensagem" seguem nas três linhas. Só se acrescentaram a base do número e o campo Tokens.
  - `R-DECISAO`, linha 8: só a data de revisão (19 para 21). A linha 11 só ganhou texto: os prós e contra por opção e a recomendação com o motivo continuam inteiros.
  - `agents/jarvis.md:109`: só inserção, depois de "custo de eficiência". A saída "decidam vocês" e as exceções de custo, acesso, exceção a regra e ato irreversível (`R-DECISAO`, "Complemento") estão intactas, e "Ordem ampla não confirma" também.
- **Números sem invenção:** `skills/modo-iniciante/SKILL.md:46-49` diz que os números nunca são inventados, exige a fonte (`medido`) ou a base (`estimado`) e proíbe número em `não medido`. Isso reduz o risco de decisão sobre dado falso; não o cria.
- **Sem custo nem acesso externo:** a fonte é `docs/kanban/entregas.md` e `docs/kanban/historico.md` (os dois no modelo de projeto, `templates/projeto/docs/kanban/`) e `forge-check transcricao custo --entregas`, que existe (`bin/forge-check:7`, `bin/forge-check:4112`) e lê transcrição em disco local. Nenhum segredo nem dado de pessoa entra na pergunta: tokens e horas são números operacionais.
- **Teste:** `tests/test_clareza.py:43-56` exige Afrouxa, Tempo e Tokens em cada opção do exemplo, as três marcas na skill e na `R-DECISAO` e o trecho no Jarvis. `python3 -m unittest tests.test_clareza`: OK.

## Achados

## Detalhe dos achados
Nenhum bloqueante. Uma recomendação (informativa, sem caminho de ataque):
- **R1 (informativa):** o teste novo confere os campos nas linhas do exemplo e as marcas na seção, mas não confere que o item 4 de `skills/modo-iniciante/SKILL.md:35` cite "tokens". Se alguém tirar "tokens" do item 4 e mantiver o exemplo, o teste continua verde. A exigência segue protegida pela `R-DECISAO:11` (o teste exige "tempo e os tokens a mais ou a menos") e pelo Jarvis. Correção mínima, se o time quiser: incluir o item 4 entre os trechos do teste. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `git diff`, `difflib` da biblioteca padrão e a suíte `tests.test_clareza`. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada); o diff é só texto e um teste, sem credencial, sem dependência nova e sem workflow.
