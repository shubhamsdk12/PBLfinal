import os

# The exact content you need
env_content = """DATABASE_URL=postgresql://postgres:PBLspendwise123@db.ayvzhxuuaqskmqqcoezd.supabase.co:5432/postgres
SUPABASE_URL=https://ayvzhxuuaqskmqqcoezd.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5dnpoeHV1YXFza21xcWNvZXpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxNzgzODMsImV4cCI6MjA4NTc1NDM4M30.6a3_SgcDrDOul0Nb9wSMbwGHRLYk9-RwUeiVCxAqo9E
SUPABASE_JWT_SECRET=ya43OjPFocwq4wzDlbyQwt++5Gbw2Awa3xpvYaPqOXNCzBTmfC4EfZinC1rd9gdRgL3jOkwHXt8t/sgHQ7rBMw==
APP_NAME=Smart Student Expense & Budget System
DEBUG=True
ENVIRONMENT=development
"""

# Write it to .env
with open(".env", "w", encoding="utf-8") as f:
    f.write(env_content)

print("✅ .env file successfully created!")
print("You can now run 'alembic upgrade head'")