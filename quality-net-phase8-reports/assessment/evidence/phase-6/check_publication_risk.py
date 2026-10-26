#!/usr/bin/env python3
"""Read-only local privacy/dependency readiness scan; values/secrets not emitted."""
from __future__ import annotations
import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[3]
filepaths=[p for p in root.rglob('*') if p.is_file() and p.suffix not in {'.zip','.png','.jpg','.jpeg','.webp','.pdf','.pyc'} and
           not any(s in p.parts for s in ('__pycache__','evidence'))]
identity=re.compile(r'(?:rakamin|ai[-_ ]interview)',re.I)
private_key=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
unsafe_assignment=re.compile(r'''(?im)^\s*(?:GEMINI_API_KEY|DB_PASSWORD|SECRET_KEY_BASE|VITE_DEV_TOKEN)\s*[:=]\s*['"]?([^'"\s#]+)''')
nonplaceholder=[];identity_files=[];key_files=[]
for p in filepaths:
 try:
  text=p.read_text(encoding='utf-8')
 except (UnicodeDecodeError,OSError):continue
 rel=str(p.relative_to(root))
 if identity.search(text) or identity.search(rel):identity_files.append(rel)
 if private_key.search(text):key_files.append(rel)
 for k in unsafe_assignment.finditer(text):
  val=k.group(1).strip()
  if rel == '.github/workflows/quality.yml' and val == 'postgres':
   continue  # disposable CI PostgreSQL service test credential, not production
  if val and not(val.startswith(('<','${','%','ENV[','test_','your_','changeme','example_')) or val in {'nil','null','REPLACE_ME'}):
   nonplaceholder.append(rel)
status={'scanned_text_files':len(filepaths),'identity_reference_paths':sorted(set(identity_files)),
        'private_key_marker_paths':sorted(set(key_files)),
        'potential_real_secret_assignment_paths':sorted(set(nonplaceholder)),
        'tracked_env_files':[str(p.relative_to(root)) for p in root.rglob('.env') if p.is_file()],
        'git_history_available':(root/'.git').exists(),
        'public_upload_ready':False,
        'limitations':['Pattern-based inspection is not a full secret scan or legal clearance.',
                       'Historical Git object scan requires a real independent Git repository.',
                       'Identifier/string sanitization must preserve runtime identifiers and requires a retest.']}
(root/'assessment/evidence/phase-6/publication-readiness.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps({'checked':len(filepaths),'identity_files':len(status['identity_reference_paths']),
                  'private_key_files':len(status['private_key_marker_paths']),
                  'possible_credential_file_count':len(status['potential_real_secret_assignment_paths']),
                  'public_upload_ready':False},indent=2))
