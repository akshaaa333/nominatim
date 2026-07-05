import json
import os

path = 'C:/Users/gopis/.gemini/antigravity-ide/brain/ac1b157f-c515-4498-baab-1f18beca94cd/.system_generated/logs/transcript.jsonl'
for line in open(path, encoding='utf-8'):
    if 'TargetFile' in line or 'write_to_file' in line:
        try:
            obj = json.loads(line)
            if 'tool_calls' in obj:
                for tc in obj['tool_calls']:
                    args = tc.get('arguments', {})
                    if 'TargetFile' in args:
                        print(f"File changed: {args['TargetFile']}")
        except:
            pass
