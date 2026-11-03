"""Reuse approved spatial audit logic on the V5.1 real parts, never overwrite V5."""
from pathlib import Path
R=Path(__file__).resolve().parents[2];source=(R/'scripts/flood/audit_final_v5.py').read_text().replace("O=R/'docs/previews/flood-control-island-g-v5'","O=R/'docs/previews/flood-control-island-g-v5-1'").replace('work/g-v5/parts.json','work/g-v51/parts.json');exec(compile(source,str(R/'scripts/flood/audit_final_v5.py'),'exec'),{'__file__':str(R/'scripts/flood/audit_final_v5.py')})
