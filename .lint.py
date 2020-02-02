import sys
	
from pylint.lint import Run
	
THRESHOLD = 7.50
	
result = Run(["venus.py"])
	
score = result.linter.stats["global_note"]
if score <= THRESHOLD:
	sys.exit(1)