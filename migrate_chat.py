#!/usr/bin/env python3
"""
Migration script to add Chat and ChatMessage tables
"""

import sqlite3
import os

def migrate_chat_tables():
    """Add Chat and ChatMessage tables to the database"""
    
    # Database file path
    db_path = 'skillswap.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("Database not found. Please run the app first to create the database.")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create Chat table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user1_id) REFERENCES user (id),
                FOREIGN KEY (user2_id) REFERENCES user (id)
            )
        ''')
        
        # Create ChatMessage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                message_type VARCHAR(20) DEFAULT 'text',
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat (id),
                FOREIGN KEY (sender_id) REFERENCES user (id)
            )
        ''')
        
        # Commit changes
        conn.commit()
        print("✅ Chat tables created successfully!")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('chat', 'chat_message')")
        tables = cursor.fetchall()
        
        if len(tables) == 2:
            print("✅ Migration completed successfully!")
        else:
            print("⚠️  Some tables may not have been created properly.")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting chat tables migration...")
    migrate_chat_tables()
    print("✨ Migration script completed!") 