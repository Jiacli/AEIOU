import sys

src = sys.argv[1]
dst = sys.argv[2]

f = open(dst, 'w')
for line in open(src, 'r'):
    if line.startswith("<"):
        continue
    else:
        f.write(line)

f.close()