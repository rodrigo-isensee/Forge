"""L51 (AQ-8): o texto do Jarvis é o núcleo `agents/jarvis.md` mais as skills para onde o texto longo se mudou. Os testes que
conferem uma frase do Jarvis leem os dois: a frase segue exigida, só mudou de arquivo."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS_DO_JARVIS = ("briefs-e-conferencia", "trabalho-em-paralelo", "falar-com-o-dono")


def texto_do_jarvis(raiz=RAIZ):
    arquivos = [raiz / "agents" / "jarvis.md"] + [raiz / "skills" / nome / "SKILL.md" for nome in SKILLS_DO_JARVIS]
    return "\n".join(a.read_text(encoding="utf-8") for a in arquivos)
