#!/usr/bin/env python3
"""
Database update script for SkillSwap
Adds the secret_code column to the PasswordReset table
"""

from app import app, db

def update_database():
    """Update the database with new secret_code column."""
    with app.app_context():
        # Create all tables (this will add the new secret_code column)
        db.create_all()
        print("Database updated successfully!")
        print("New secret_code column has been added to PasswordReset table.")

if __name__ == "__main__":
    update_database() 