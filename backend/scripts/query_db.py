import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.base import SessionLocal
from app.models.generation_model import GenerationModel
from app.models.generate_page import GeneratePage

db = SessionLocal()
print("=== Level 1 Generate Pages ===")
for p in db.query(GeneratePage).filter(GeneratePage.level == 1).all():
    print(f"ID: {p.id}, category_name: {p.category_name}, title: {p.title}")

print("\n=== Models ===")
for m in db.query(GenerationModel).all():
    print(f"ID: {m.id}, name: {m.name}, work_type: {m.work_type}")
