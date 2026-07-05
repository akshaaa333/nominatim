import os

with open("app/repositories/place_repository.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    '''Place.district.ilike(f"{raw_query}%")''',
    '''(Place.district == raw_query) | (Place.district == raw_query.title())'''
)

with open("app/repositories/place_repository.py", "w", encoding="utf-8") as f:
    f.write(code)
