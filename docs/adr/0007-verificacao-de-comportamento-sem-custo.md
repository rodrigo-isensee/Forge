# 0007 - Verificação de comportamento sem custo

Estado: vigente. Data: 2026-10-12.
Propósito: verificar o comportamento dos agentes sem gastar dinheiro com IA. Público: quem mantém o Forge. Revisão: 2026-10-12.

## Contexto
As avaliações com IA (`claude plugin eval`) foram removidas na 0.2.1 por exigirem API paga; decisão do usuário: nada que custe dinheiro (`R-CUSTO`). Sem elas, só os testes estruturais protegem a fábrica, e eles não dizem nada sobre o que os agentes fazem numa sessão real (ex.: lançar 5 agentes, abrir PR sem QA).

## Decisão
1. **Sem IA paga em nenhuma etapa** do CI nem dos testes locais. Nenhum teste chama modelo.
2. **Hooks testados por fixture** (ADR 0003): o comportamento garantido por hook é verificado de forma determinística, com JSON de entrada e resultado esperado.
3. **Verificador offline de transcrições:** sessões reais gravadas (os arquivos `.jsonl` que o Claude Code já salva) viram casos de teste em `tests/transcricoes/`. O verificador (Python, biblioteca padrão, dentro do `forge-check`) lê a sequência de chamadas de ferramenta e confere propriedades nomeadas pelo ID da regra (ADR 0002), por exemplo: `R-TETO` (nunca mais agentes simultâneos que o teto); `R-REVIEW` e `R-QA` (`gh pr create` só depois de pareceres válidos); `R-MAIN` (nenhum `git push` para a `main`); prompt de delegação com as seis seções do Jarvis.
4. **Anonimização obrigatória** antes de versionar, feita por um passo do `forge-check`: mantém só o nome da ferramenta, os parâmetros necessários às propriedades e os horários; troca caminhos, nomes, e-mails e nomes de projeto por marcadores; descarta saídas de ferramenta e textos do usuário. O teste de neutralidade passa a cobrir `tests/transcricoes/`.
5. **Coleta voluntária:** quem quiser contribuir com uma transcrição roda a anonimização e abre PR (ADR 0006). Uma transcrição que viola uma propriedade é registrada como caso esperado de falha e motiva um hook ou uma mudança de agente.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| `claude plugin eval` no CI | Testa o efeito de mudar um prompt | Custa dinheiro; removido por decisão do usuário |
| Eval local com a assinatura do usuário | Sem cobrança extra direta | Gasta a cota do usuário e não roda no CI; fica fora do portão |
| Só testes estruturais (hoje) | Zero custo | Não observam comportamento |

## Consequências
- Mais fácil: regressões de processo aparecem em dados reais, sem custo.
- Limite: o verificador olha o passado; não prevê o efeito de uma mudança de prompt antes de ela ser usada. A proteção preventiva fica com os hooks.
- Risco: vazamento de dado de projeto numa transcrição. Mitigação: anonimização por lista de permissão, teste de neutralidade e revisão no PR.
- O formato do `.jsonl` do Claude Code pode mudar: o leitor isola o formato num só módulo, e os fixtures guardam a versão de origem.
