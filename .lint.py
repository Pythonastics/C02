import sys

from os import listdir
from os.path import join
from pylint.lint import Run
	
THRESHOLD = 7.50

cogs = [join("cogs", c) for c in listdir("./cogs") if c.endswith(".py")]
utils = [join("cogs.utls", c) for c in listdir("./cogs/utils") if c.endswith(".py")]
	
result = Run(["bot.py", *cogs, *utils])
	
score = result.linter.stats["global_note"]
if score <= THRESHOLD:
	sys.exit(1)