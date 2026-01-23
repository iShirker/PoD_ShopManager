"""
Database migrations that run on application startup.
Handles schema changes that need to be applied before the app runs.
"""
from sqlalchemy import text, inspect


def run_startup_migrations(db, app):
    """
    Run all startup migrations.

    Args:
        db: SQLAlchemy database instance
        app: Flask application instance
    """
    with app.app_context():
        try:
            _migrate_supplier_connections_multiple_accounts(db)
            _migrate_api_key_column_size(db)
            _migrate_user_products_tables(db)
            app.logger.info("Startup migrations completed successfully")
        except Exception as e:
            app.logger.error(f"Startup migration error: {e}")
            # Don't raise - allow app to start even if migrations fail
            # The error will be logged for debugging


def _migrate_supplier_connections_multiple_accounts(db):
    """
    Migration to support multiple accounts per supplier type.

    Changes:
    1. Drops the unique constraint on (user_id, supplier_type) if it exists
    2. Adds account_name, account_email, account_id columns if they don't exist
    """
    inspector = inspect(db.engine)

    # Check if the table exists
    if 'supplier_connections' not in inspector.get_table_names():
        return  # Table doesn't exist yet, will be created by db.create_all()

    # Get existing columns
    existing_columns = {col['name'] for col in inspector.get_columns('supplier_connections')}

    # Get existing constraints
    unique_constraints = inspector.get_unique_constraints('supplier_connections')
    constraint_names = {c['name'] for c in unique_constraints if c['name']}

    with db.engine.connect() as conn:
        # Drop the unique constraint if it exists
        # The constraint might be named differently depending on how it was created
        possible_constraint_names = [
            'unique_user_supplier',
            'uq_supplier_connections_user_id',
            'supplier_connections_user_id_supplier_type_key',  # PostgreSQL auto-generated name
        ]

        for constraint_name in possible_constraint_names:
            if constraint_name in constraint_names:
                try:
                    # PostgreSQL syntax
                    conn.execute(text(f'ALTER TABLE supplier_connections DROP CONSTRAINT IF EXISTS {constraint_name}'))
                    conn.commit()
                    print(f"Dropped constraint: {constraint_name}")
                except Exception as e:
                    # SQLite doesn't support DROP CONSTRAINT, but also doesn't have the constraint
                    print(f"Could not drop constraint {constraint_name}: {e}")

        # Also try to drop any index that might enforce uniqueness
        indexes = inspector.get_indexes('supplier_connections')
        for idx in indexes:
            if idx.get('unique') and set(idx.get('column_names', [])) == {'user_id', 'supplier_type'}:
                try:
                    idx_name = idx.get('name')
                    if idx_name:
                        conn.execute(text(f'DROP INDEX IF EXISTS {idx_name}'))
                        conn.commit()
                        print(f"Dropped unique index: {idx_name}")
                except Exception as e:
                    print(f"Could not drop index: {e}")

        # Add new columns if they don't exist
        new_columns = [
            ('account_name', 'VARCHAR(255)'),
            ('account_email', 'VARCHAR(255)'),
            ('account_id', 'VARCHAR(255)'),
        ]

        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                try:
                    conn.execute(text(f'ALTER TABLE supplier_connections ADD COLUMN {col_name} {col_type}'))
                    conn.commit()
                    print(f"Added column: {col_name}")
                except Exception as e:
                    # Column might already exist or other error
                    print(f"Could not add column {col_name}: {e}")


def _migrate_api_key_column_size(db):
    """
    Migration to increase api_key and api_secret column sizes.
    
    Printify tokens can be 1000+ characters, so we need to change
    VARCHAR(500) to TEXT to support longer tokens.
    """
    inspector = inspect(db.engine)
    
    # Check if the table exists
    if 'supplier_connections' not in inspector.get_table_names():
        return  # Table doesn't exist yet, will be created by db.create_all()
    
    # Get existing columns with their types
    existing_columns = {col['name']: col for col in inspector.get_columns('supplier_connections')}
    
    with db.engine.connect() as conn:
        # Check and migrate api_key column
        if 'api_key' in existing_columns:
            api_key_type = str(existing_columns['api_key']['type'])
            # Check if it's VARCHAR(500) or similar small size
            if 'VARCHAR' in api_key_type.upper() or 'CHARACTER VARYING' in api_key_type.upper():
                # Check the length
                if '500' in api_key_type or 'CHARACTER VARYING(500)' in api_key_type:
                    try:
                        # PostgreSQL: ALTER COLUMN ... TYPE TEXT
                        conn.execute(text('ALTER TABLE supplier_connections ALTER COLUMN api_key TYPE TEXT'))
                        conn.commit()
                        print("Migrated api_key column from VARCHAR(500) to TEXT")
                    except Exception as e:
                        print(f"Could not migrate api_key column: {e}")
        
        # Check and migrate api_secret column
        if 'api_secret' in existing_columns:
            api_secret_type = str(existing_columns['api_secret']['type'])
            # Check if it's VARCHAR(500) or similar small size
            if 'VARCHAR' in api_secret_type.upper() or 'CHARACTER VARYING' in api_secret_type.upper():
                # Check the length
                if '500' in api_secret_type or 'CHARACTER VARYING(500)' in api_secret_type:
                    try:
                        # PostgreSQL: ALTER COLUMN ... TYPE TEXT
                        conn.execute(text('ALTER TABLE supplier_connections ALTER COLUMN api_secret TYPE TEXT'))
                        conn.commit()
                        print("Migrated api_secret column from VARCHAR(500) to TEXT")
                    except Exception as e:
                        print(f"Could not migrate api_secret column: {e}")


def _migrate_user_products_tables(db):
    """
    Migration to create user_products and user_product_suppliers tables.
    These tables are created by db.create_all() but this migration ensures
    they exist and handles any schema updates.
    """
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    # Tables will be created by db.create_all() if they don't exist
    # This migration is mainly for documentation and future schema changes
    if 'user_products' not in table_names or 'user_product_suppliers' not in table_names:
        # Tables don't exist yet, will be created by db.create_all()
        print("User products tables will be created by db.create_all()")
        return

    # Future schema migrations can be added here
    print("User products tables exist")
