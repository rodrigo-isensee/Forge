---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: 0b2e8d6f8ca3671cdba187ec985a5b15afe65b0b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-forge-check-ci-verde (E47.3)

Escopo: `git diff 004ce869..0b2e8d6f` (13 arquivos): `bin/forge-check` (PARECER-SO-COM-CI-VERDE e META85-FC-RESTOS), `agents/jarvis.md` (passo 5), fragmento do changelog, mutantes e testes.

Gatilhos: controle do Forge (`bin/forge-check`, portão `pr` do merge), integração com o `gh` (leitura de PR e checks), texto de agente (`agents/jarvis.md`).

## Achados

## Sondas

## Só aperta: confirmação por escrito
**Confirmo: a mudança em `bin/forge-check` só aperta; nada afrouxa portão, catraca nem hook.** Motivo, item por item:
- `checks_ruins` (`bin/forge-check:1529`) é extração do corpo de `checks_do_head`, com o mesmo comportamento: "no checks reported" vira lista vazia, saída ilegível vira a violação "não lidos", os exigidos do destino seguem exigindo `pass`. Equivalente ao de antes.
- `suite_do_parecer` (`bin/forge-check:2127`, chamada em `:2052`) só faz `saida +=`: acrescenta violação a review e QA que já aprovavam; nunca remove linha nem muda o `veredito_do_parecer`. Liga só com `suite is not None`, só em branch de trabalho e só no Forge. Sem `gh`, sem rede, sem PR, outro head, nenhum check ou check pendente: `ci_verde_no_head` (`:1546`) dá False (falha fechada). Base ilegível: `modulos_tocados` dá None e a prova não vale (falha fechada).
- O `adiar` (`--previo` e passo 1 do `forge-fechar`, `:1590`) só avisa no stderr: antes não havia exigência nenhuma ali, e os passos 4 e 6 do fechar seguem exigindo os checks verdes.
- Catraca do CI, hook `parecer` e promoção chamam `cmd_pr` sem `suite` (padrão None): idênticos a antes.
- `arquivo_do_parecer_novo` (`:3566`) só muda o caminho impresso pelo `parecer novo` (só leitura); o slug passa por `NOME_SEGURO_DE_BRIEF` (sem barra, sem `..` no início), fora disso cai no `<pedido>.md`. Sem travessia.
- Brief de `merge-integracao` (`:9099`) ganha uma linha de texto que restringe o merge a `origin/<base>`; `base` vem de `choices=BASES_DO_FLUXO`.
- `tests/test_meta85_item_arquivos.py` passa a rodar com `python3 -I` e ambiente limpo: aperta o isolamento do teste.
- `tests/mutantes/z075-pr-previo.json` M3, M7 e M8 só acompanham a assinatura nova; as guardas e os testes citados são os mesmos.
- `agents/jarvis.md` passo 5: restringe a retomada da instância à revalidação com `revalida: sim`; não dispensa portão.

## Detalhe dos achados
Sem achado. Conferências:
- Injeção de comando: `gh` roda por lista de argumentos, sem shell, com teto de tempo e `stdin` nulo (`gh_json`); a branch vem do git (não começa com `-`).
- ReDoS: `PROVA_DA_SUITE` (`:2100`) e `MODULO_DE_TESTE_DO_DIFF` (`:2101`) sem quantificador ambíguo; sonda local com 100 mil caracteres: até 0,004 s.
- Segredo: 0 ocorrências de token, chave privada ou credencial nas linhas acrescidas.
- Informativo (sem caminho de ataque novo): a linha `- suíte: <sha40> rc=0 módulos=...` é declaração do revisor, não verificação; quem pode escrevê-la já podia aprovar sem ela, e a autoria do parecer segue com o hook. É a decisão do dono (a ferramenta dirigida não é portão); o CI do PR segue exigido no merge pelo `checks_do_head`.
- Testes novos rodados localmente: `tests.test_forge_check_pr` e `tests.test_aq5_parecer_novo`, 53 testes, OK. A suíte inteira é do CI do PR (sem PR aberto no head na hora deste parecer).

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; a entrega não toca workflow nem dependência.
