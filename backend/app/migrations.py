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
            _migrate_template_products_pricing(db)
            _migrate_subscription_and_new_tables(db, app)
            _migrate_user_preferred_theme(db)
            _migrate_plan_names_pro_master(db)
            _migrate_subscription_billing_interval(db)
            _migrate_subscription_auto_renew(db)
            _migrate_user_free_trial_used_at(db)
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


def _migrate_template_products_pricing(db):
    """
    Migration to add pricing configuration fields to template_products table.
    
    Adds:
    - alias_name: Unique alias name for product within template
    - pricing_mode: Pricing mode (per_config, per_size, per_color, global)
    - prices: JSON field for storing prices
    - global_price: Global price when pricing_mode is 'global'
    """
    inspector = inspect(db.engine)
    
    # Check if the table exists
    if 'template_products' not in inspector.get_table_names():
        return  # Table doesn't exist yet, will be created by db.create_all()
    
    # Get existing columns
    existing_columns = {col['name'] for col in inspector.get_columns('template_products')}
    
    with db.engine.connect() as conn:
        # Add new columns if they don't exist
        new_columns = [
            ('alias_name', 'VARCHAR(255)'),
            ('pricing_mode', 'VARCHAR(20)'),
            ('prices', 'JSON'),
            ('global_price', 'FLOAT'),
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                try:
                    if col_type == 'JSON':
                        # Use TEXT for SQLite, JSON for PostgreSQL
                        db_url = str(db.engine.url)
                        if 'postgresql' in db_url or 'postgres' in db_url:
                            conn.execute(text(f'ALTER TABLE template_products ADD COLUMN {col_name} JSON'))
                        else:
                            # SQLite or other databases
                            conn.execute(text(f'ALTER TABLE template_products ADD COLUMN {col_name} TEXT'))
                    else:
                        conn.execute(text(f'ALTER TABLE template_products ADD COLUMN {col_name} {col_type}'))
                    conn.commit()
                    print(f"Added column: {col_name}")
                except Exception as e:
                    # Column might already exist or other error
                    print(f"Could not add column {col_name}: {e}")
        
        # Set default pricing_mode for existing rows
        if 'pricing_mode' not in existing_columns:
            try:
                conn.execute(text("UPDATE template_products SET pricing_mode = 'global' WHERE pricing_mode IS NULL"))
                conn.commit()
                print("Set default pricing_mode for existing rows")
            except Exception as e:
                print(f"Could not set default pricing_mode: {e}")


def _migrate_subscription_and_new_tables(db, app):
    """
    Create new tables (subscription, order, pricing, discount) and seed subscription_plans.
    db.create_all() creates missing tables; this migration seeds data.
    """
    from app.models import SubscriptionPlan
    db.create_all()
    if SubscriptionPlan.query.count() > 0:
        return
    plans = [
        {
            'slug': 'free_trial',
            'name': 'Free Trial',
            'price_monthly': 0,
            'price_yearly': None,
            'limits': {
                'stores': 1,
                'products': 50,
                'listings': 20,
                'orders_total': 100,
                'mockups_total': 20,
                'storage_mb': 100,
                'seo_suggestions': 20,
                'discount_programs': 1,
                'discount_products': 10,
            },
            'features': {'api_access': False, 'priority_support': False},
        },
        {
            'slug': 'starter',
            'name': 'Starter',
            'price_monthly': 19.99,
            'price_yearly': 199.99,
            'limits': {
                'stores': 1,
                'products': 200,
                'listings': 100,
                'orders_monthly': 500,
                'mockups_monthly': 100,
                'storage_mb': 500,
                'seo_suggestions_monthly': 100,
                'discount_programs': 2,
                'discount_products': 25,
            },
            'features': {'api_access': False, 'priority_support': False},
        },
        {
            'slug': 'growth',
            'name': 'Pro',
            'price_monthly': 49.99,
            'price_yearly': 499.99,
            'limits': {
                'stores': 3,
                'products': 1000,
                'listings': 500,
                'orders_monthly': 2000,
                'mockups_monthly': 500,
                'storage_mb': 2048,
                'seo_suggestions_monthly': 500,
                'discount_programs': 5,
                'discount_products': 100,
            },
            'features': {'api_access': 'read_only', 'priority_support': False},
        },
        {
            'slug': 'scale',
            'name': 'Master',
            'price_monthly': 99.99,
            'price_yearly': 999.99,
            'limits': {
                'stores': 10,
                'products': 5000,
                'listings': 2500,
                'orders_monthly': 10000,
                'mockups_monthly': 2000,
                'storage_mb': 10240,
                'seo_suggestions_monthly': 2000,
                'discount_programs': 15,
                'discount_products': 500,
            },
            'features': {'api_access': True, 'priority_support': True},
        },
    ]
    for p in plans:
        plan = SubscriptionPlan(
            slug=p['slug'],
            name=p['name'],
            price_monthly=p['price_monthly'],
            price_yearly=p.get('price_yearly'),
            limits=p['limits'],
            features=p['features'],
            is_active=True,
        )
        db.session.add(plan)
    db.session.commit()
    app.logger.info("Seeded subscription_plans")


def _migrate_user_preferred_theme(db):
    """Add preferred_theme to users if missing."""
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('users')}
    if 'preferred_theme' in existing:
        return
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE users ADD COLUMN preferred_theme VARCHAR(20)'))
            conn.commit()
            print("Added users.preferred_theme")
        except Exception as e:
            print(f"Could not add preferred_theme: {e}")


def _migrate_plan_names_pro_master(db):
    """Rename Growth -> Pro, Scale -> Master in subscription_plans."""
    if 'subscription_plans' not in inspect(db.engine).get_table_names():
        return
    with db.engine.connect() as conn:
        try:
            conn.execute(text("UPDATE subscription_plans SET name = 'Pro' WHERE slug = 'growth'"))
            conn.execute(text("UPDATE subscription_plans SET name = 'Master' WHERE slug = 'scale'"))
            conn.commit()
        except Exception as e:
            print(f"Could not migrate plan names: {e}")


def _migrate_subscription_billing_interval(db):
    """Add billing_interval to user_subscriptions."""
    inspector = inspect(db.engine)
    if 'user_subscriptions' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('user_subscriptions')}
    if 'billing_interval' in existing:
        return
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE user_subscriptions ADD COLUMN billing_interval VARCHAR(20)'))
            conn.commit()
            print("Added user_subscriptions.billing_interval")
        except Exception as e:
            print(f"Could not add billing_interval: {e}")


def _migrate_subscription_auto_renew(db):
    """Add auto_renew to user_subscriptions."""
    inspector = inspect(db.engine)
    if 'user_subscriptions' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('user_subscriptions')}
    if 'auto_renew' in existing:
        return
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE user_subscriptions ADD COLUMN auto_renew BOOLEAN NOT NULL DEFAULT 1'))
            conn.commit()
            print("Added user_subscriptions.auto_renew")
        except Exception as e:
            print(f"Could not add auto_renew: {e}")


def _migrate_user_free_trial_used_at(db):
    """Add free_trial_used_at to users."""
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('users')}
    if 'free_trial_used_at' in existing:
        return
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE users ADD COLUMN free_trial_used_at TIMESTAMP'))
            conn.commit()
            print("Added users.free_trial_used_at")
        except Exception as e:
            print(f"Could not add free_trial_used_at: {e}")
