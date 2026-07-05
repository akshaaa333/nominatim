import json, sys

files = ['place_repository.py', 'goride_provider.py', 'search_pipeline.py', 'base_ranker.py', 'place_ranker.py', 'category_ranker.py', 'pincode_ranker.py', 'admin_area_ranker.py', 'query_intent.py']
path = 'C:/Users/gopis/.gemini/antigravity-ide/brain/b9c8e3ba-fbc5-46ba-b270-b226fad26495/.system_generated/logs/transcript_full.jsonl'
for line in open(path, encoding='utf-8'):
    try:
        obj = json.loads(line)
        if 'tool_calls' in obj:
            for tc in obj['tool_calls']:
                args = tc.get('arguments', {})
                if 'TargetFile' in args and any(f in args['TargetFile'] for f in files):
                    print(f"Tool: {tc['function']['name']}, File: {args['TargetFile']}")
    except Exception as e:
        pass
