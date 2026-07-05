import os

with open("app/utils/search_pipeline.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("logger.info(f\"--- DEBUG PIPELINE", "print(f\"--- DEBUG PIPELINE")
code = code.replace("logger.info(f\"Intent:", "print(f\"Intent:")
code = code.replace("logger.info(f\"Repository Method:", "print(f\"Repository Method:")
code = code.replace("logger.info(f\"Repository Candidate Count:", "print(f\"Repository Candidate Count:")
code = code.replace("logger.info(f\"Candidate IDs", "print(f\"Candidate IDs")
code = code.replace("logger.info(f\"Provider Candidate Count", "print(f\"Provider Candidate Count")
code = code.replace("logger.info(f\"Merged Count:", "print(f\"Merged Count:")
code = code.replace("logger.info(f\"Ranked Count:", "print(f\"Ranked Count:")
code = code.replace("logger.info(f\"Final Returned Count:", "print(f\"Final Returned Count:")
code = code.replace("logger.info(f\"-----------------------------------\")", "print(f\"-----------------------------------\")")

with open("app/utils/search_pipeline.py", "w", encoding="utf-8") as f:
    f.write(code)
