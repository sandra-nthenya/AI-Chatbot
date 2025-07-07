"""
Supabase setup script for AI Chat Support
This script helps configure and initialize the Supabase database
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import DATABASE_URL
from models import Base

def setup_supabase():
    """Setup Supabase database connection and tables"""
    
    if not DATABASE_URL or DATABASE_URL.startswith("sqlite"):
        print("⚠️  No Supabase URL configured. Using SQLite for development.")
        print("To use Supabase:")
        print("1. Create a Supabase project at https://supabase.com")
        print("2. Get your database URL from Settings > Database")
        print("3. Set DATABASE_URL in your .env file")
        return False
    
    try:
        # Test connection
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print(f"✅ Connected to database: {result.fetchone()[0]}")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Create initial tenant
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO tenants (id, name, domain, api_key, is_active)
                VALUES (
                    'default-tenant',
                    'Default Organization',
                    'default.local',
                    'default-api-key',
                    true
                )
                ON CONFLICT (id) DO NOTHING
            """))
            conn.commit()
            print("✅ Default tenant created")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Ensure your Supabase project is active")
        print("3. Check if your IP is allowed in Supabase settings")
        return False

def create_env_template():
    """Create a template .env file"""
    env_content = """# AI Chat Support Backend Configuration

# Database
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-SUPABASE-ANON-KEY]

# API Keys
GEMINI_API_KEY=[YOUR-GEMINI-API-KEY]
OPENAI_API_KEY=[YOUR-OPENAI-API-KEY]

# Security
SECRET_KEY=your-secret-key-change-in-production

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# RAG Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("📝 Created .env.template file")
    print("Copy this to .env and fill in your actual values")

if __name__ == "__main__":
    print("🚀 AI Chat Support - Supabase Setup")
    print("=" * 40)
    
    # Create env template if it doesn't exist
    if not os.path.exists('.env.template'):
        create_env_template()
    
    # Try to setup database
    if setup_supabase():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Configure your API keys in .env file")
        print("2. Start the server: python main.py")
        print("3. Test the API endpoints")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("You can still run the application with SQLite for development") 