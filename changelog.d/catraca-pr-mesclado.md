### Corrigido
- Catraca: a conferência do PR mesclado volta a liberar a promoção develop → homolog quando cada arquivo protegido vem de um PR já rotulado pelo dono e mesclado por squash (o CI passa o merge de teste como head, e a cadeia de primeiro pai procurada era só esse merge; foi o que pediu o rótulo de novo no #310 e no #317), e diz o motivo quando não libera.
