#!/usr/bin/env python3
"""
Database update script for SkillSwap
Adds the PasswordReset table to the existing database
"""

from app import app, db

def update_database():
    """Update the database with new tables."""
    with app.app_context():
        # Create all tables (this will add the new PasswordReset table)
        db.create_all()
        print("Database updated successfully!")
        print("New PasswordReset table has been created.")

if __name__ == "__main__":
    update_database() 