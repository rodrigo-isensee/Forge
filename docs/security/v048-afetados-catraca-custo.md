---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-afetados-catraca-custo
commit: f4ae675c22dd8b656a5dc28a7db85f1e3e3d1e99
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (#960, AFETADOS-CATRACA-E-CUSTO, E9.1 e E9.2)

E9.5, 1ª rodada completa no head f4ae675c (base ed6e6dbf). Lido: o diff inteiro de `bin/forge-testes`, `tests/test_afetados_catraca_custo.py`, as specs de mutante, e o consumidor `.githooks/pre-push` (função `afetados`, que lê a 1ª linha do `--listar`).

## Gatilhos
Gatilhos: código de controle (bin/forge-testes, sensível da catraca), hook de envio (plano do pre-push opt-in).

## Achados
- A1 (recomendado) bin/forge-testes:584 · tests/catraca.py apagado ou trocado por link no diff: custo_e_catraca devolve ((), False) em silêncio e o plano segue sem a catraca nem aviso; o diff toca um protegido e a catraca não roda no computador (falha aberta, sem aviso)
- A2 (recomendado) bin/forge-testes:552 · PASTAS_DA_CATRACA não tem scripts/, que está em PASTAS_CUSTO e SENSIVEIS da catraca: um `claude -p` novo em scripts/ passa o --afetados local (sem catraca) e só o CI o barra, o defeito que o E9.1 quer evitar

## Sondas

## Detalhe dos achados
Conferências do brief:
- **Hook, bin/ ou protegido sempre leva a catraca, inclusive acima do limite.** O bool `catraca` vem de `custo_e_catraca` (bin/forge-testes:580) antes do corte e o corte do E9.2 (bin/forge-testes:1336) só troca `detalhe`, mantendo `extra` (o teste de custo) e o bool; a catraca roda depois dos módulos (bin/forge-testes:1363-1365) e o código de saída dela entra no resultado (`codigo or da_catraca`). Sondas no head: `--afetados --listar` com `hooks/novo.py`, `bin/forge-check`, `.github/workflows/ci.yml`, `.githooks/pre-push` e `tests/neutralidade.py`: todos acima de 1.000 testes, todos com `test_hooks_volta_corpus` no plano e a linha "catraca no diff". Plano vazio com catraca imprime `dirigido ()`, que o pre-push aceita e executa (não cai no "nada a rodar"). PROTEGIDOS ilegível conta como tocada (falha fechada, teste `test_protegidos_ilegiveis_contam_como_tocados`). Diff com renomeação lista os dois caminhos (`--no-renames`, bin/forge-testes:340) e arquivo não versionado entra.
- **Nome de arquivo do diff não vira execução.** Os caminhos só passam por `startswith`, comparação, `re.fullmatch` e `Path`; os nomes de módulo vêm de regex `[a-z0-9_-]` e precisam existir em `tests/`; a catraca roda com argv em lista, `-I`, sem shell, e o único argumento variável é `--base` (do próprio usuário, não do diff). Sonda: `hooks/$(touch PWNED).py` e `bin/a;touch PWNED2` como caminhos: nenhum arquivo criado. Contagem de testes por `ast.parse`, sem importar o módulo.

A1: severidade baixa. Caminho: quem envia uma branch que apaga `tests/catraca.py` ou o troca por link roda o `--afetados` local sem catraca e sem aviso. Sem ganho real de ataque: o envio local é opt-in (`FORGE_PREPUSH_SUITE=afetados`) e o CI roda a catraca da base (`CATRACA_DA_BASE`), que é o portão. O link ignorado é decisão do autor (`test_catraca_em_link_nao_conta`); o que falta é não ser silencioso. Correção mínima: quando o arquivo falta ou é link e algum caminho está em hooks/ ou bin/ ou é o próprio `tests/catraca.py`, imprimir no stderr "catraca ausente ou em link: não rodou; o CI a roda" (ou devolver código de erro), com teste. Esforço P. Dono: tech-lead (autor).

A2: severidade baixa. Sonda reproduzida numa cópia descartável: commit de `scripts/novo-sonda.sh` com `claude -p "oi"`; `forge-testes --afetados --listar` dá `dirigido (test_forge, test_indice_forge, test_oraculo_sempre_atual, test_oraculo_v047)` sem catraca, rc 0; `tests/catraca.py --base ed6e6dbf` dá rc 1 com `R-CUSTO: claude-print em scripts/novo-sonda.sh:2`. O E9.1 pede hooks/, bin/ e protegido ao pé da letra (cumprido); a lacuna é o mesmo defeito do processo em `scripts/` (e `.github/` fora dos protegidos). Correção mínima: ler da catraca, pelo mesmo `ast`, também `PASTAS_CUSTO` (`hooks/`, `bin/`, `scripts/`, `.github/`) e somar a `PASTAS_DA_CATRACA`, com teste para `scripts/x.sh`. Se o dono quiser manter a letra do E9.1, vira cartão. Esforço P. Dono: tech-lead (autor).

Fora do meu domínio, ao tech-lead (não é achado de segurança): acima do limite, a regra do MAPA de `hooks/` ainda leva uns 1.900 testes no plano cortado (sonda `hooks/novo.py`: 3724 no plano, 1821 para o CI), acima dos 1.000 do ajuste do dono; e o `--base` da catraca confere o HEAD, não a ref enviada, num envio de várias refs.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Teste novo rodado: `tests.test_afetados_catraca_custo`, 19 testes, OK. Suíte inteira: CI do #960 no f4ae675c, suíte 1/5 a 5/5, bateria e instalação verdes; a catraca vermelha só pelo texto do PR (R-CONTRIB: "Projeto de origem" e "Como medir" vazios), não pelo código, a corrigir pelo autor no corpo do PR. Ferramentas ausentes no PATH (lacuna, não instaladas): varredor de segredo, SAST, auditor de dependências e linters de workflow; o diff não toca workflow nem dependência.
