import sys
import re

sh ="www.lanzous.com"
sh = re.sub(r"lanzou(\w)", "lanzoub", sh)
print(sh)

print(sys.argv)
