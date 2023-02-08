import re
import subprocess

process = subprocess.Popen('python all/main.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out, _ = process.communicate()
out = out.decode('utf-8')
print(out)

with open("os") as f:
    os = f.read()

with open("README.md") as f:
    op=re.sub(rf"(```{os.strip()}\n)(.+?)(?=```)", rf"\1{out}".rstrip() + "\n",
        f.read(), 0, re.MULTILINE | re.DOTALL)

with open("README.md", "w") as f:
    f.write(op)