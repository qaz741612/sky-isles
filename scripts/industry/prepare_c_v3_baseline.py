"""Extract only three pinned original PR17 files into local QA scratch space."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
for name in ['public/models/industry-youth-c/industry-youth-c.glb','src/data/industry-youth-collision.json','src/world/industry-youth.js']:
    p=ROOT/'work/v3-baseline'/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('wb')as f:subprocess.run(['git','show','0c7cab7:'+name],cwd=ROOT,stdout=f,stderr=subprocess.PIPE,check=True)
print('Prepared 3 pinned PR17 baseline files locally; no binary output')
