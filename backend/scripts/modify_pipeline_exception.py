import re

with open("app/utils/search_pipeline.py", "r", encoding="utf-8") as f:
    code = f.read()

replacement = """if isinstance(res_list, list):
                      all_results.extend(res_list)
                  elif isinstance(res_list, Exception):
                      import traceback
                      print(f"PROVIDER EXCEPTION: {res_list}\\n{''.join(traceback.format_exception(None, res_list, res_list.__traceback__))}")
"""

code = code.replace("""if isinstance(res_list, list):
                      all_results.extend(res_list)""", replacement)

with open("app/utils/search_pipeline.py", "w", encoding="utf-8") as f:
    f.write(code)
