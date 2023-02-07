import sys
import re
with open("os") as f:
    os = f.read()
with open("README.md") as f:
    op=re.sub(f"(```{os}\n)(.+?)(?=```)",rf"\1{sys.stdin.read()}".rstrip() + "\n",f.read(),0,re.MULTILINE|re.DOTALL)
with open("README.md", "w") as f:
    f.write(op)