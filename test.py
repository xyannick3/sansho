import re

pattern = re.compile(r"https?://(?:www\.)?(twitter|x)\.com/([a-zA-Z0-9_]+)/status/(\d+)(?:\?.*)?")
text = "Check this tweet https://twitter.com/shitpostgate/status/1896111987366732158?s=46&t=9fHcI6gObDucRpq6TEnkgw"

matches = re.findall(pattern, text)
print("Matched URLs:", matches)
