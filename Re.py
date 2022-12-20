import re

raw = "1669159803543;49a7cd4b5857;123456;95063;,43;2 ";

print(raw.replace("", ""))
print(re.sub("", "", raw))

result = re.sub("[\u0000-\u001F]", "", raw)
print(result.split(";"))

