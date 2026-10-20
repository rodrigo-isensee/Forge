---
tipo: revisao-seguranca
contrato: 1
pedido: conf-correcao
branch: melhoria/conf-correcao
commit: 13099560a326fc268c47cce68cc6a190678f855a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: conf-correcao

Etapa E1.3 (`R-SEGURANCA`). Escopo: `git diff 74e5bb75dfc87d54d9228e8357c7f027a3646c64 13099560a326fc268c47cce68cc6a190678f855a` inteiro (`bin/forge-check`, `agents/conferente.md`, `agents/jarvis.md`, `docs/regras/R-BRIEF.md`, `tests/test_forge.py`, `tests/apoio_versao_defasada.py`, `changelog.d/conf-correcao.md`), conferido contra as mitigações mínimas e os 18 casos de abuso do modelo de ameaças da E0.2 (`~/.forge-contrib/docs/propostas/security/conf-correcao.md`). Revisor: outra instância do security-engineer, não o autor. Sondas numa cópia própria do commit em `$TMPDIR` (`git archive`), sem trocar o HEAD da worktree.

## Gatilhos
`bin/forge-check` (subcomando `brief`: o novo `brief mensagem` e `decisoes_cobradas`) e `agents/conferente.md` são controles do Forge (`R-SEGURANCA`, gatilho controles do Forge; o conferente incluído). `docs/regras/R-BRIEF.md` muda o texto da regra.

## Achados

## Detalhe dos achados

### Mitigações mínimas da E0.2: conferidas no código e nos testes

| Mitigação | Evidência no código (13099560) | Teste |
|---|---|---|
| M1.1 brief só em `docs/briefs/`, sem atalho do cwd, link para fora recusado | `cmd_brief_mensagem` usa só `caminho_de_brief` (`bin/forge-check:2933`), que passa por `dentro_da_raiz` (realpath, :754); `--anterior` idem | `MensagemRecusada.test_arquivo_fora_de_docs_briefs_rc_2` (travessia, absoluto, link, `README.md`), `test_arquivo_relativo_ao_cwd_nao_vale`, `test_anterior_fora_de_docs_briefs_rc_2` |
| M1.2 mesmo buffer conferido, medido, hasheado e impresso | uma leitura (`f.read(TETO_DO_BRIEF + 1)`), o mesmo `conteudo` vai a `avaliar_brief`, a `Bytes:`, a `Brief-sha256:` e ao `sys.stdout.buffer.write` (:2980) | `MensagemAprovada.test_saida_integral_com_hash_e_bytes`, `test_brief_sem_quebra_de_linha_final_sai_igual_byte_a_byte`, `test_o_hash_da_mensagem_e_o_da_linha_arquivo_do_comando` |
| M1.3 recusa de delimitador em qualquer posição, controle (fora de `\n` e `\t`), Cf, e também Zl e Zp | `recusa_do_texto` (:2901), antes de qualquer impressão | `test_delimitador_em_qualquer_posicao_rc_2`, `test_controle_e_formato_rc_2` (`\r`, ESC, NUL, U+0085, U+202E, U+200B, U+2066), `test_tab_e_acento_nao_recusam` |
| M1.4 cabeçalho de uma linha por campo | `--pedido` com controle recusado, `--etapa` por `sem_controle` (:2929), `--destino` por `forge:[a-z0-9-]+`, `--ref` por `[^\s-]\S*` (:2896), delimitador no cabeçalho recusado (:2977) | `test_campos_do_cabecalho_ficam_em_uma_linha`, `test_pedido_com_quebra_de_linha_nao_forja_cabecalho`, `test_destino_e_ref_invalidos_rc_2` (ver R1) |
| M1.5 rc 1 e rc 2 sem o texto | rc 1 imprime só as linhas que reprovam e `resultado: reprovado`; rc 2 só o motivo | `test_brief_reprovado_pelo_comando_rc_1_sem_o_texto` |
| M1.6 a mensagem vai ao conferente e não o substitui; as duas comparações | `agents/conferente.md:44`, `agents/jarvis.md:64`, `docs/regras/R-BRIEF.md:11` | `TextosDoAgenteEDaRegra.test_mensagem_vai_ao_conferente_e_nao_o_substitui` |
| M1.7 guarda de versão; nenhuma opção que grava | `avaliar_versao`: `a.alvo in ("gerar", "mensagem")`; o comando só lê; `hooks/conformidade.json` não muda | `GuardaDeVersao.test_mensagem_bloqueia_como_gerar`, `FerramentaDefasadaNoForge` (cinco subcomandos), `test_so_le_e_imprime_nao_altera_o_disco` |
| M2.1 travessia e link no registro citado; cópia principal na frente | `REGISTRO_VALIDO` exige `docs/pedidos/<nome>.md` sem `/` a mais; `ler_registro` (:2744) com ordem cópia principal, raiz, `RAIZES_DE_BRIEF` (:2747) e `dentro_da_raiz` com realpath; o primeiro que tem o nome decide, sem cair no seguinte; ausente reprova | `DecisoesCobradas.test_travessia_absoluto_e_link_para_fora_nao_sao_lidos` (nada do arquivo de fora no `brief` nem no `gerar`), `test_registro_ausente_reprova`, `test_a_copia_da_branch_nao_vence_a_principal`, `test_prefixo_forge_contrib_e_cobrado_e_a_copia_principal_vence` |
| M2.2 recorte silencioso: nada some | toda referência `.md` numa linha de decisão do dono fora de `docs/pedidos/`, e toda referência `.md` numa linha `D-<ID> = ` do pedido, sai `decisões: fonte fora da regra ... (não verificável)` (:2791); não reprova pelo comando e o `conferente.md` manda conferir por `grep -n` | `test_fonte_fora_da_regra_nunca_some` (o caso D-ETAPAS-INST), `test_fonte_fora_da_regra_nao_reprova_por_si` |
| M2.3 contradição literal continua do conferente | `decisões: ok (...; presença; contradição conferida pelo conferente)`; `conferente.md` item 2 | `test_decisoes_do_comando_e_contradicao_do_conferente` |
| M2.4 trechos citados escapados | `nome_seguro(chave_da_decisao(...))` e `sem_controle` nas linhas copiadas pelo `gerar` e pela volta | `test_linha_com_aspas_e_controle_sai_numa_linha_escapada` |
| M2.6 tetos | 1 MB por registro (lido com `read(teto + 1)`), 20 fontes; ambos reprovam | `test_registro_grande_demais_reprova`, `test_fontes_demais_reprova` |
| M3.1 `tardio:` reprova | `agents/conferente.md:19` e `:60` (o prefixo conta como o campo), `docs/regras/R-BRIEF.md:14` | `test_tardio_na_regra_e_no_campo_do_veredito`, `test_ordem_da_primeira_passada_e_tardio_no_agente` |
| M3.2 a rodada de confirmação não proíbe o tardio | `agents/conferente.md:52` | `test_rodada_de_confirmacao_nao_proibe_registrar_tardio` |
| M3.3 e M3.4 leitura fechada nas `fonte:` do comando; fidelidade, contradição e etapa sempre do conferente | `agents/conferente.md:18` | `test_ordem_de_leitura_fixa_e_so_as_fontes_do_comando` |

A troca, em `conferir_volta`, de `ler_pedido_brief(...)["decisoes"]` por `cobradas["fontes"]` não afrouxa: cobra as mesmas linhas do pedido e acrescenta as dos registros; a chave de comparação ganhou `sem_controle` dos dois lados. O `--etapa` deixou de ter `choices` no argparse, mas `main` revalida a lista para `gerar`. Não afrouxa nenhum controle: o comando cobra mais que antes e o que fica fora sai visível.

**Casos de abuso:** os 18 têm teste (1 a 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 e 18, marcados nos testes acima; 10 em `GuardaDeVersao` e `FerramentaDefasadaNoForge`). Rodei na cópia do commit as classes `MensagemAprovada`, `MensagemRecusada`, `DecisoesCobradas`, `DecisoesNaVolta`, `GuardaDeVersao`, `TextosDoAgenteEDaRegra` e `FerramentaDefasadaNoForge`: 57 testes, OK. A suíte inteira roda no pre-push deste envio.

**Rede (`R-CUSTO`):** o diff não acrescenta acesso à rede; os únicos `subprocess` novos são dos testes, que chamam o próprio `forge-check` local; o `forge-check` continua só com `git` local.

### Recomendações (não bloqueiam)

**R1 (baixa) separador de linha Unicode e controle nos campos do cabeçalho.** Evidência: `bin/forge-check:2929` e `:2930` (`sem_controle` tira só `\x00-\x1f` e `\x7f`) e `:2896`, `:2974`, `:2976` (`--ref` vai cru ao cabeçalho). Sonda: `--etapa` com U+2028, U+2029 ou U+0085 entre `Arquivo: docs/briefs/outro.md` e `Brief-sha256: fff...` sai com rc 0 e, lido por quem quebra linha em Unicode (`str.splitlines`), o cabeçalho tem dois `Arquivo:` e dois `Brief-sha256:`; U+202E passa no `--etapa`; `--ref` aceita ESC, DEL e U+202E. O caso de abuso 6 só testa `\n`. Caminho de ataque: o Jarvis induzido por texto num pedido monta `--etapa` com o separador; o conferente lê dois `Arquivo:`. Ganho real baixo: o texto entre os delimitadores continua o do brief verdadeiro, e a comparação com o `cat` exigida em M1.6 (`agents/conferente.md:44`) reprova se o conferente seguir o `Arquivo:` falso (falha fechada); um Jarvis comprometido também poderia escrever a mensagem à mão. Por isso, recomendação. Correção mínima: aplicar `recusa_do_texto` (ou recusar Cc, Cf, Zl, Zp e U+0085) a `--etapa`, `--pedido` e `--ref`, e estender o teste do caso 6 a U+2028, U+0085 e U+202E. Esforço P. Dono: tech-lead, numa volta futura ou no próximo pedido do conferente.

**R2 (baixa) ordem das raízes do registro no layout do Forge.** Evidência: `bin/forge-check:2747`. A ordem cópia principal, raiz, `RAIZES_DE_BRIEF` é a que a M2.1 pediu e a mesma do `caminho_do_pedido` (A1). No Forge, a cópia principal não tem `docs/pedidos/` e os pedidos moram em `~/.forge-contrib/docs/pedidos/`; rodado com `--raiz` numa worktree cuja branch traga `docs/pedidos/<nome>.md` com o nome de um registro citado, a cópia da branch vence a de `~/.forge-contrib`, e o `gerar` copiaria linhas forjadas como decisões do dono. Caminho pouco provável: o Jarvis e o conferente rodam da cópia principal, e um `docs/pedidos/` numa branch do Forge aparece no diff do PR. Correção mínima: quando a cópia principal não tem `docs/pedidos/`, consultar `RAIZES_DE_BRIEF` antes da raiz (vale também para o pedido). Esforço P. Dono: tech-lead. A lacuna é do modelo de ameaças da E0.2, que fixou essa ordem.

**R3 (informativa) referência de segundo nível e caminho absoluto.** Linha de decisão de um registro citado que cita outro `.md` é cobrada como linha, mas a fonte dela não sai como `fonte fora da regra` (um nível, como decidido; antes desta mudança também não se lia o segundo nível, então não afrouxa). Registro citado por caminho absoluto (inclusive de `~/.forge-contrib` expandido) sai `registro citado ausente` e reprova: falso positivo possível, mas falha fechada.

**Invariante para `tardio:`:** em pedido próprio, não agora. O texto já é protegido pelos testes `test_tardio_na_regra_e_no_campo_do_veredito` e `test_ordem_da_primeira_passada_e_tardio_no_agente`, que falham se o trecho sumir de `agents/conferente.md` ou de `docs/regras/R-BRIEF.md`; o invariante em `tests/config.json` acrescenta a exigência de destaque no título do PR para afrouxar, que é a proteção da fábrica para trechos de regra. Entrar agora exigiria uma volta à E1.1 fora do E1 a E4 decididos ("isso", 2026-10-20). Sugestão: junto do cartão DECISAO-ANCORA ou dos cartões do conferente depois da retrospectiva (INVARIANTE-GATILHO).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `grep`, sondas com `unittest` numa cópia do commit em `$TMPDIR`. `gitleaks`, `semgrep`, `zizmor` e `osv-scanner` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow). Nada instalado; nenhuma rede (`R-CUSTO`).
