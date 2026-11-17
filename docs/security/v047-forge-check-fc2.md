---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-forge-check-fc2
commit: e1aff90260eba1e97fa153ddcd9b5e8127e5945f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047-forge-check-fc2 (E2.436, revalidado em E2.604)

Revalidação por delta no head e1aff902 (E2.604): `forge-check parecer delta` sobre `b7a180d6..e1aff902`. O delta próprio é só `skills/qa-testing/SKILL.md` (frases encurtadas, regra e IDs mantidos: `R-QA`, `R-REVIEW`, `R-SEGURANCA`, casos de abuso e oráculo intactos), o mutante I20 reancorado (teste, fora do domínio) e `tests/test_volta_por_delta.py` com `remoto_sem_manutencao(self.origem)` (grava config local no bare de teste, sem `GIT_*` herdadas, sem config global; sem alcance fora do tmp). O `bin/forge-check` que o delta lista veio da develop (E1.252, E2.316, FC-DOCS-CAMINHO), sem commit próprio desde b7a180d6; o diff de `base_do_delta_em_dia`/`linhas_de_ids_do_fora` é o já revisado, e o A1 foi corrigido (bin/forge-check:3211, "salvo o git fetch"). A2 segue recomendado, sem promoção. Sem `critério mudou`.

Parecer anterior, para contexto:

Parecer completo (não havia parecer anterior) do diff `58dfa2ab..b7a180d6`: `bin/forge-check` (`base_do_delta_em_dia`, `linhas_de_ids_do_fora`, `fora_do_escopo_do_pedido`), `skills/qa-testing/SKILL.md`, `changelog.d/v047-forge-check-fc2.md`, `tests/test_volta_por_delta.py` e as duas especificações de mutantes. Sem gatilho de credencial, dado pessoal nem workflow; o gatilho é controle do Forge (o delta da revalidação dos portões e a conferência de corte do brief, `R-SEGURANCA`, `R-BRIEF`, `R-REVIEW`).

## Gatilhos
Gatilhos: controle do Forge (forge-check: delta da revalidação de parecer e corte de escopo do brief de volta), rede (git fetch novo)

## Achados
- A2 (recomendado) bin/forge-check:2989 · Com a busca bem-sucedida e um merge de outra branch no intervalo (fora[0] ainda fora da base nova), a linha diz `base: atualizada` sem o `aviso:`; o delta segue fechado (nada some), mas o leitor não sabe que o merge conta inteiro. Reconferir a ancestralidade depois do fetch.

## Sondas

## Detalhe dos achados (A1 resolvido no head e1aff902)
**Análise do `git fetch` novo (bin/forge-check:2967-2989).** Caminho examinado: quem roda `forge-check parecer delta` (portão na revalidação) com a `origin/<base>` local atrasada. Fronteiras: (1) o nome da base vem da lista branca `BASES_DO_DELTA` (bin/forge-check:2944), conferida em `cmd_parecer_delta` antes de qualquer git, então o refspec `+refs/heads/<base>:refs/remotes/origin/<base>` não aceita injeção de opção nem de ref; (2) o fetch passa pelo `git()` único (bin/forge-check:520), que tira as `GIT_*` herdadas (deixa só as `GIT_CONFIG_*`, como no `ls-remote` já aceito) e tem limite de 5 s; o `TimeoutExpired` vira aviso e rc de falha vira aviso (base inalterada); (3) o que encolhe o delta continua sendo o `escopo_pelo_primeiro_pai` (bin/forge-check:2490), que só desconta o merge cujo segundo pai é ancestral da base e mantém a resolução de conflito e o `-s ours`. Logo, o fetch só traz a cópia local para o estado do servidor, cuja `develop`/`homolog` é protegida (`R-FLUXO`, `R-MAIN`); um autor não consegue esconder mudança própria fazendo o merge de outra branch (falha fechada, provada por `test_sem_rede_o_merge_fica_no_delta_com_aviso`). O fetch não é chamado por hook (`hooks/parecer.py` usa `base_do_delta`, sem rede) nem está na lista do conferente (bin/forge-check:6453-6456, sem `parecer`). Sem custo (`R-CUSTO`): fetch do remoto do próprio projeto.
O `+` (atualização forçada da ref de acompanhamento) é o comportamento normal do `git fetch` e não amplia poder: quem reescreve a base do servidor já tem mais que isso.

**A1** · evidência bin/forge-check:112 (`(PARECER-CONTEUDO; só leitura)`) frente a bin/forge-check:3156-3157 · caminho de ataque: nenhum direto; quem roda o delta em ambiente que deveria ser só leitura pode não esperar a escrita em `.git/refs` e a rede · severidade: informativa · correção mínima: no texto de uso, "só leitura, salvo o `git fetch origin <base>` da base local atrasada" · esforço P · dono: tech-lead (autor do FC2).

**A2** · evidência bin/forge-check:2984-2989: `depois != antes` basta para a linha `base:`, sem conferir `e_ancestral(fora[0], depois)` · caminho de ataque: nenhum que esconda código (o `escopo_pelo_primeiro_pai` conta o merge de outra branch inteiro); o risco é de leitura: o revisor lê `base: ... trazia o que ela não tinha` e supõe que o merge saiu do delta · severidade: baixa · correção mínima: depois do fetch, se algum de `fora` ainda não é ancestral de `depois`, imprimir também o `aviso:` · esforço P · dono: tech-lead.

**Fora do escopo compacto (bin/forge-check:3637-3654).** Os ids saem das chaves de `dados["etapas"]`, já extraídas por expressão de id (sem texto livre do pedido), então a remoção do `sem_controle` não abre injeção de controle ou de quebra de linha no brief. A conferência de corte (`conferir_corte`, `referencias_do_item`) lê cada id da linha agrupada; a remoção de um id da linha reprova (`test_..._e14` e `corte: sem marca "E2.1"` em `test_conferencia_reprova_anterior_bloco_e_achado`), e o pedido de 600 etapas passa na conferência com `E4.600` reconhecido (sem confusão de prefixo `E4.6`/`E4.60`). As linhas de corte do dono (`MARCA_DE_CORTE`) continuam copiadas do anterior. A perda do texto das etapas no brief é só de contexto: o texto segue no pedido.

**Suíte.** Rodado na raiz do clone no head e1aff902: `python3 -m unittest tests.test_volta_por_delta.DeltaComBaseAtrasada`: 3 testes, OK (4,6 s); o módulo inteiro (102 testes) passou em b7a180d6 e o delta de teste desde então é 2 linhas. A suíte inteira roda no CI do PR, aberto só depois dos pareceres (PR-DEPOIS-DOS-PARECERES); a falha conhecida de `test_reval_delta` vem do #576 na develop, fora deste diff.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura estática e o módulo de teste do item. `gitleaks`, Semgrep e `zizmor` não foram usados (diff sem segredo, sem workflow; a varredura roda no CI).
