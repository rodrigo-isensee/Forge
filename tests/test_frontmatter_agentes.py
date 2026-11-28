"""FRONTMATTER-AGENTES (E2.151): todo frontmatter de agents/*.md e stacks/*/agents/*.md lê como YAML, com name e description.

Sem PyYAML (biblioteca padrão): confere o subconjunto que os agentes usam, `chave: valor` em escalar simples ou entre
aspas. Escalar simples com ': ' ou ' #' no meio não é YAML válido e o carregador descarta os campos em silêncio.
"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS = sorted(RAIZ.glob("agents/*.md")) + sorted(RAIZ.glob("stacks/*/agents/*.md"))
CHAVE = re.compile(r"^([A-Za-z_][\w-]*):(?: +(.*))?$")


def erros_do_frontmatter(texto: str) -> list[str]:
    linhas = texto.split("\n")
    if linhas[0].rstrip() != "---":
        return ["sem abertura '---'"]
    try:
        fim = next(i for i in range(1, len(linhas)) if linhas[i].rstrip() == "---")
    except StopIteration:
        return ["sem fechamento '---'"]
    erros, campos = [], {}
    for n, linha in enumerate(linhas[1:fim], start=2):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        m = CHAVE.match(linha)
        if not m:
            erros.append(f"linha {n}: não é 'chave: valor'")
            continue
        chave, valor = m.group(1), (m.group(2) or "").strip()
        campos[chave] = valor
        if valor[:1] in ("'", '"'):
            q = valor[0]
            if len(valor) < 2 or valor[-1] != q or (q == "'" and re.search(r"(?<!')'(?!')", valor[1:-1])):
                erros.append(f"linha {n}: aspas de '{chave}' não fecham como escalar")
        elif valor[:1] in ("[", "{", "|", ">", "&", "*", "!", "%", "@", "`"):
            continue
        elif ": " in valor or valor.endswith(":") or " #" in valor:
            erros.append(f"linha {n}: '{chave}' tem ': ' ou ' #' sem aspas (não lê como YAML)")
    for obrigatorio in ("name", "description"):
        if not campos.get(obrigatorio):
            erros.append(f"falta '{obrigatorio}'")
    return erros


class FrontmatterAgentes(unittest.TestCase):
    def test_ha_agentes(self):
        self.assertGreaterEqual(len(ARQUIVOS), 12)

    def test_todo_frontmatter_le_como_yaml(self):
        for p in ARQUIVOS:
            with self.subTest(agente=str(p.relative_to(RAIZ))):
                self.assertEqual(erros_do_frontmatter(p.read_text(encoding="utf-8")), [])

    def test_detecta_dois_pontos_sem_aspas(self):
        ruim = '---\nname: x\ndescription: Dono do "como": tudo\n---\n'
        self.assertTrue(erros_do_frontmatter(ruim))
        self.assertEqual(erros_do_frontmatter("---\nname: x\ndescription: 'a: b'\n---\n"), [])


def _fm(*linhas: str) -> str:
    """Frontmatter válido (name e description) mais as linhas dadas; o fechamento vem no fim."""
    return "\n".join(["---", "name: x", "description: y", *linhas, "---", ""])


class RamosDeErro(unittest.TestCase):
    """Um caso por ramo de erro de erros_do_frontmatter; cada um cai se o seu ramo for removido."""

    def test_sem_abertura(self):
        self.assertEqual(erros_do_frontmatter("name: x\ndescription: y\n---\n"), ["sem abertura '---'"])

    def test_sem_fechamento(self):
        self.assertEqual(erros_do_frontmatter("---\nname: x\ndescription: y\n"), ["sem fechamento '---'"])

    def test_linha_que_nao_e_chave_valor(self):
        self.assertEqual(erros_do_frontmatter(_fm("- item")), ["linha 4: não é 'chave: valor'"])

    def test_aspas_duplas_sem_fechar(self):
        erros = erros_do_frontmatter(_fm('nota: "abc'))
        self.assertEqual(len(erros), 1)
        self.assertIn("aspas de 'nota' não fecham", erros[0])

    def test_aspas_simples_sem_fechar(self):
        erros = erros_do_frontmatter(_fm("nota: 'abc"))
        self.assertEqual(len(erros), 1)
        self.assertIn("aspas de 'nota' não fecham", erros[0])

    def test_valor_de_uma_aspa_so(self):
        erros = erros_do_frontmatter(_fm('nota: "'))
        self.assertEqual(len(erros), 1)
        self.assertIn("aspas de 'nota' não fecham", erros[0])

    def test_aspa_simples_solta_dentro_de_aspas_simples(self):
        erros = erros_do_frontmatter(_fm("nota: 'it's'"))
        self.assertEqual(len(erros), 1)
        self.assertIn("aspas de 'nota' não fecham", erros[0])
        self.assertEqual(erros_do_frontmatter(_fm("nota: 'it''s'")), [])

    def test_escalar_terminado_em_dois_pontos(self):
        erros = erros_do_frontmatter(_fm("nota: abc:"))
        self.assertEqual(len(erros), 1)
        self.assertIn("'nota' tem ': ' ou ' #'", erros[0])

    def test_escalar_com_espaco_e_cerquilha(self):
        erros = erros_do_frontmatter(_fm("nota: abc #d"))
        self.assertEqual(len(erros), 1)
        self.assertIn("'nota' tem ': ' ou ' #'", erros[0])

    def test_indicador_yaml_pula_a_checagem_de_escalar(self):
        for valor in ("[a: b]", "{a: b}", "| a: b", "> a #b", "&a b: c", "*a b: c"):
            with self.subTest(valor=valor):
                self.assertEqual(erros_do_frontmatter(_fm(f"nota: {valor}")), [])

    def test_comentario_e_linha_em_branco_sao_ignorados(self):
        self.assertEqual(erros_do_frontmatter(_fm("# a: b: c", "", "   ", "  # d e")), [])

    def test_falta_name(self):
        self.assertEqual(erros_do_frontmatter("---\ndescription: y\n---\n"), ["falta 'name'"])

    def test_falta_description(self):
        self.assertEqual(erros_do_frontmatter("---\nname: x\n---\n"), ["falta 'description'"])

    def test_obrigatorio_com_valor_vazio_conta_como_falta(self):
        self.assertEqual(erros_do_frontmatter("---\nname:\ndescription: y\n---\n"), ["falta 'name'"])


if __name__ == "__main__":
    unittest.main()
