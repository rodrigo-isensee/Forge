# Referência lida sob demanda (QA)

Parte da skill `qa-testing`, num arquivo próprio para o que o `qa-engineer` carrega sempre ficar longe do teto do
orçamento de instrução (`docs/regras/orcamento.json`; diretriz 25 do dono: regra existente não se apaga nem se resume; o
que não cabe muda de arquivo, com ponteiro). A `SKILL.md` diz quando ler cada seção; o texto aqui vale como o de lá.

## Modelo do plano de testes (`docs/qa/<feature>.md`)
Leia ao abrir o plano.

```markdown
# Plano de testes - <feature>
Links: especificação de UX, contrato da API, plano técnico.

## Escopo
O que está e o que não está coberto.

## Cenários
| ID | Cenário | Tipo | Prioridade | Automatizado |
|---|---|---|---|---|
| CT-01 | Login com credenciais válidas | E2E | Alta | sim |

## Dados de teste
Usuários, permissões e fixtures necessários.

## Resultado da execução
Data, ambiente, aprovados/falhos, links para bugs.
```

## Teste-oráculo do portão: onde, como e o review
Leia ao escrever o oráculo (EXT-1, no Forge) ou ao revisar um.
- **Onde e como:** `tests/test_oraculo_<pedido>.py` (nome minúsculo, `[a-z0-9_]`), só em `melhoria/*`, num commit próprio
  que só toca o oráculo. O hook `conformidade` barra a escrita do autor (tech-lead, dev, jarvis) nesse padrão; o
  bin/forge-testes põe todo oráculo em todo plano dirigido. Autocontido: só biblioteca padrão, o código sob teste e
  utilitários do próprio arquivo, sem `skip`, `skipIf`, `expectedFailure` nem ambiente que decida o que testa. O commit
  vermelho do oráculo chega ao autor por `git fetch` local, nunca vai sozinho ao remoto.
- **Review:** o oráculo é contrato. O parecer do review cita o sha dele e diz se cobre os casos de abuso do modelo de
  ameaças; o portão não aprova contra o próprio oráculo sem essa leitura.

## Mutantes declarados: equivalente e cobertura
Leia ao declarar um mutante equivalente ou ao ler a saída do `--cobertura`.
- **Equivalente:** o mutante equivalente se declara no campo `equivalente`, com a justificativa, e sai na linha
  `equivalente: <id> · <justificativa>`, sem rodar; com `testes`, roda, e o que eles matam é inválido; o equivalente não
  prova: a spec só de equivalentes sem `testes` sai 2 e, no `--cobertura`, a condição coberta só por ele sai
  `só equivalente`, rc 1.
- **Saídas do `bin/forge-mutante --cobertura --base <Base-sha>`:** a condição Python mudada sem mutante declarado sai
  "declarado, não provado"; shell e outros saem `não coberto: <arquivo>`; as `isentas` da spec, até 8, saem
  `isenta · arq:L · motivo`, e a que não cruza, `isenta velha`, rc 1.

## Modelo do relatório de bug (`docs/qa/bugs/<id>-<titulo>.md`)
Leia ao abrir o relatório.

```markdown
# <id> - <título curto>
- Severidade: crítica | alta | média | baixa
- Responsável sugerido: agente de desenvolvimento da stack
- Ambiente: branch/commit, navegador

## Passos para reproduzir
1. ...

## Resultado esperado
## Resultado obtido
## Evidência
Log, screenshot ou trace da ferramenta de E2E.
```
