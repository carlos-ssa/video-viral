"""Confere o planejamento no manifesto: 0 consistente, 1 corrigir, 2 aguarda dados declarados.

Não mede criatividade ou desempenho. Use em produção/planejamento completo, não em ajustes pontuais.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_manifest, project_dir


def plan_problems(m):
    errors = []
    if not isinstance(m, dict):
        return ["manifesto precisa ser um objeto"], []
    brief = m.get("brief") or {}
    if not isinstance(brief, dict):
        return ["brief precisa ser um objeto"], []
    missing = brief.get("missing_inputs") or []
    if not isinstance(missing, list) or any(not isinstance(x, str) or not x.strip() for x in missing):
        return ["brief/missing_inputs inválidos"], []
    if brief.get("objective") not in ("alcance", "consideracao", "conversao", "entretenimento"):
        errors.append("brief.objective ausente ou inválido")
    required = ["audience", "problem_or_desire", "benefit", "desired_action"]
    if brief.get("objective") in ("consideracao", "conversao") or m.get("format") in ("produto", "ugc"):
        required.append("offer")
    if brief.get("objective") == "conversao":
        required.append("cta_destination")
    for key in required:
        if not isinstance(brief.get(key), str) or not brief[key].strip():
            if key not in missing:
                errors.append(f"brief.{key}: preencha ou declare em brief.missing_inputs")
    hooks = m.get("hook_candidates")
    if not isinstance(hooks, list) or len(hooks) < 5 or any(not isinstance(x, dict) or not x for x in hooks):
        errors.append("hook_candidates precisa conter cinco candidatos audiovisuais")
    if not isinstance(m.get("hook"), str) or not m["hook"].strip():
        errors.append("hook vencedor ausente")
    tools = m.get("tool_plan")
    if not isinstance(tools, list) or not tools:
        errors.append("tool_plan ausente")
    else:
        for item in tools:
            if (not isinstance(item, dict) or not (item.get("tool") or item.get("ferramenta"))
                    or item.get("status") not in ("integrado", "validado-neste-projeto", "adaptacao", "planejado")):
                errors.append("tool_plan: informe ferramenta e status real da integração")
                break
    stack = m.get('stack')
    if isinstance(stack, dict) and stack.get('version') == '2.0.0':
        allowed = {entry['id'] for entry in json.loads((Path(__file__).resolve().parents[1] / 'assets/stack.json').read_text(encoding='utf-8'))['modules']}
        selected = stack.get('modules')
        if stack.get('compositor') != 'hyperframes' or not isinstance(selected, list) or any(not isinstance(x, str) or x not in allowed for x in selected):
            errors.append('stack v2: compositor precisa ser hyperframes e módulos devem pertencer ao catálogo')
        elif not {'hyperframes', 'gsap', 'ffmpeg'}.issubset(selected):
            errors.append('stack v2: declare hyperframes, gsap e ffmpeg no núcleo')
        if isinstance(tools, list) and any(not isinstance(item, dict) or item.get('module') not in allowed for item in tools):
            errors.append('tool_plan v2: cada entrada precisa de module com ID do catálogo')
    research = m.get("research")
    if not isinstance(research, dict) or not isinstance(research.get("sources"), list):
        errors.append("research.sources precisa ser uma lista (vazia quando não houver dados)")
    return errors, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project")
    args = ap.parse_args()
    try:
        errors, missing = plan_problems(load_manifest(project_dir(args.project)))
    except (OSError, ValueError, TypeError) as exc:
        ap.error(str(exc))
    status = "corrigir" if errors else "aguarda-dados" if missing else "consistente"
    print(json.dumps({"status": status, "errors": errors, "missing_inputs": missing,
                      "aesthetic_quality_or_performance_verified": False}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 2 if missing else 0)


if __name__ == "__main__":
    main()
