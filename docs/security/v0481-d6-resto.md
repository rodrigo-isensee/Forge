---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 50a40e28844435d4bf43c8b23d3880e1b37af7b9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 E11.21 (#877, D6 parte a: hook `salvar`, volta E11.18 pela opção b do dono)

## Gatilhos
Gatilhos: hook novo fora do sandbox, controle do git (R-VERIFY core.hooksPath, R-MAIN); a rede no hook (ADR 0003 item 2) e o push automático saem neste delta.

Delta lido (`forge-check parecer delta`, `1afd54b5..50a40e28`): os commits da branch são `cfd24cee` (`hooks/salvar.py`, `hooks/hooks.json`, emenda D6 da ADR 0003, `docs/regras/R-LIMITES.md`, `tests/test_hooks.py`, specs `v0481-d6-resto*.json`), `b6c98cb2` (ADR 0003 e `R-LIMITES.md`), `88fc382a` e `50a40e28` (só `tests/test_hooks.py`, classe `SalvarAoParar`). O resto do intervalo vem do merge da develop (`9f264141`), com parecer próprio em cada PR; não é deste. Já lido antes: `config_permitida`, `plano`, `arquivos_a_salvar`, `ler_brief`, `de_escrita`.

Testes: `python3 -m unittest tests.test_hooks.SalvarAoParar` no clone em `50a40e28`, 29 OK. A suíte não foi rodada aqui. O CI do PR no head exato tem verdes as suítes 3.12 e 3.14 (partes 1 a 5), bateria (passos), verificações longas, python 3.14, instalação, teto de pulados e árvore provada. Os vermelhos são três, e nenhum é do código:
- `bateria (pareceres)`: espera os pareceres (R-REVIEW e R-SEGURANCA ainda em `1afd54b5`, R-QA reprovado).
- `bateria`: é o agregado dos jobs e só herda a falha de `pareceres`.
- `catraca`: a causa, lida no log do run 45652375891, é R-QA, guarda de `hooks/salvar.py` mudada sem mutante provado. O `:127` só tem o M29 equivalente e o `:156` (`__name__ == "__main__"`) não tem mutante. Isso se resolve com um mutante ou uma isenção do autor, ou com o rótulo `afrouxa-regra`, que o PR já pede ao dono pelo R-VERIFY. Não é achado de segurança.

- ci: 50a40e28844435d4bf43c8b23d3880e1b37af7b9 verde

Estado dos achados anteriores (parecer em `1afd54b5`):
- **A4 (bloqueante, base da varredura): resolvido. O envio saiu.** `salvar` (`hooks/salvar.py:133`) faz só `add` e `commit --only` e devolve a linha do log. No arquivo não há `push`, `fetch`, `ls-remote` nem chamada ao script de varredura (grep). A base em `HEAD^`/`refs/remotes/origin` não existe mais. S4 e S5 dependiam do envio e não se aplicam. Prova: `test_salva_so_o_escopo_na_copia` (`tests/test_hooks.py:4393`) confere que nada chega ao remoto. `test_branch_ja_no_remoto_fica_como_esta` (`:4580`) confere que a branch remota e a `origin/<branch>` da cópia ficam iguais, ou seja, sem push e sem fetch. O segredo de commit local anterior volta ao caminho de sempre: o `pre-push` do envio varre desde o sha que o próprio git lhe passa.
- **M8 e M9 do QA (fixture não rastreado): resolvidos.** `docs/a.md2` agora é rastreado no `setUp` (`:4317`) e fica fora do commit como ` M docs/a.md2`, o que prova que o arquivo exato do escopo não vale como prefixo. Os remotos bare rodam com `remoto_sem_manutencao` (`:4314`), sem `gc` em segundo plano no teste.
- **A5 (recomendado, corrida na config): superado pelo delta.** A janela de até 50 s (varredura mais push) acabou. Depois de `config_permitida` (`:54`, chamada no `plano`) restam só `symbolic-ref`, `rev-parse`, `status`, `add` e `commit`, chamadas locais seguidas. Isso equivale à reconferência logo antes do commit que eu tinha pedido. O que sobra, um processo hostil do agente gravando a config nesses milissegundos, depende de agente hostil e de processo que sobreviva à parada. Esse resíduo vai na linha `Melhoria vista` do relatório, para a emenda registrá-lo.

## Achados

## Sondas

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:**
  - Some a rede do hook. A ADR 0003 item 2 volta a valer sem exceção (emenda, regra 3, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md:115`).
  - Some o push automático fora do sandbox. Com ele saem a varredura de segredo com base em ref local, que o agente grava, e o script de varredura rodando fora do sandbox.
  - O critério de reversão passa a incluir "qualquer chamada de rede dele".
  - O envio do trabalho salvo passa pelo `pre-push` inteiro, no fechamento ou no próximo envio do autor.
  - Nenhum run de CI é disparado pelo hook (R-CUSTO).
- **Neutro:**
  - `BASH_ENV` e `ENV` deixam a lista do ambiente (`:38`). O hook não chama mais o bash, e esse ambiente vem do processo do Claude Code, não do agente.
  - O texto do `hooks.json` e do `indice-forge.md`.
  - `R-MAIN` e `R-FLUXO`: a guarda das branches de integração continua no `plano` (`:102`).
  - `config_permitida`, `GIT_SEGURO` (`:26`) e o prazo total não mudaram.
  - Os testes trocam o remoto pelo commit da cópia e não perdem caso de segurança: config do agente, hooks do git da cópia, `GIT_*` herdadas, operação em andamento e brief ambíguo continuam testados.
  - Saem os mutantes M26, M36 e M37, junto com as guardas do envio que eles mutavam.
  - O `R-LIMITES.md` volta ao texto da base (`b6c98cb2`). A exceção ao R-VERIFY fica só na regra 4 da emenda. Para os agentes, a regra fica inteira, sem texto que leiam como licença.
- **Afrouxa (declarado, à espera do dono):**
  - O R-VERIFY: o commit WIP na cópia roda com `core.hooksPath=/dev/null`, o que pula o `pre-commit` do projeto. O `pre-push` e o CI o cobrem, e está declarado no título do PR.
  - Os dois invariantes de teste da emenda: `salvar` no grupo `{0}` e `timeout` 60 no `SubagentStop`.
  - Não declarado: nada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O merge ainda depende do rótulo `afrouxa-regra` do dono para o R-VERIFY e do parecer de QA. Ferramentas: `gitleaks`, Semgrep, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna). A revisão foi manual, com grep do arquivo do hook e a classe `SalvarAoParar` rodada localmente.
