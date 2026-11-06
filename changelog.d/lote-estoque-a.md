### Alterado
- O security-engineer diz o teto de 300 caracteres do achado (ACHADO-TETO-DOC, parcial: falta o tech-lead.md).
- Texto de agentes e skills: guarda do diff com um mutante por linha e teste do ramo de falha (tech-lead, engineering-practices), QA como fonte de achados recorrentes (qa-testing) e brief seguinte fixado só depois de gravar a etapa em curso (jarvis) (AQ1-TEXTO)
- Texto de agentes (T2, T4, T5, T6 do ciclo 3 do aq, AQ3-TEXTO): o arquiteto classifica o afrouxamento e marca gatilhos_seguranca no plano; o agile-coach usa as marcas medido, estimado e não medido, separa propor de implementar e lê o git sem escrever; os agentes da stack node-react param sem especificação, citam R-CONFORMIDADE e tomam o contrato do esquema compartilhado, e o pronto sugerido passa a pnpm (projetos novos); o UX só registra a validação com a frase literal do usuário e marca a acessibilidade como lida ou medida
- PR de release da homologação para a main: o tech-lead abre só com o portão verde, lista antes de criar e edita o PR existente (só título e corpo, sem mudar a base), sem mesclar; check do PR em andamento espera e, se falhar por causa externa, reexecuta o mesmo sha (F22, texto em R-FLUXO, ci-cd e tech-lead)
- o `forge-fechar` diz, na parada do passo 5, se o rótulo `afrouxa-regra` foi pedido pelo título ou por item marcado do corpo e, sem `--esperar-rotulo`, manda rodar de novo com ela depois que o dono aplicar o rótulo (FECHAR-ESPERAR-ROTULO)
- O modelo de pedido traz a etapa do security-engineer para o pedido que prevê invariante novo em tests/config.json (INVARIANTE-GATILHO).
- Os modelos de parecer dizem que o teto de 300 caracteres do achado não conta o prefixo, e o de segurança do Forge avisa da neutralidade (MODELOS-PARECER-AVISOS-2).
- docs: pareceres de review, segurança e QA do E8 (CONFERENTE-LEITURA-GIT) e do QA do E9 (PARECER-UX-LIVRE), mais o teste de encadeamento e escape do conferente e a spec de mutação `versao-033-qa`.
- A pergunta ao dono diz, em palavras, se o custo de cada opção fica maior ou menor que o das outras (PERGUNTA-MAIOR-MENOR).
- Os agentes security-engineer e qa-engineer dizem o teto de 300 caracteres do achado (ACHADO-TETO-DOC; o tech-lead.md fica para o lote dele).

### Adicionado
- A skill trabalho-em-paralelo manda avisar, antes de delegar, que editar agents/*.md exige a regra de permissão, quando ela não estiver configurada (PERMISSAO-AGENTES-MD).
- A skill trabalho-em-paralelo manda avisar, antes de delegar, que editar agents/*.md pode exigir uma regra de permissão (PERMISSAO-AGENTES-MD).
