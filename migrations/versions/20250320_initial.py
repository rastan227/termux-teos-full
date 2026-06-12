"""Initial schema

Revision ID: 20250320_initial
Revises: 
Create Date: 2025-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20250320_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users table
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(64), nullable=True),
        sa.Column('first_name', sa.String(128), nullable=False),
        sa.Column('last_name', sa.String(128), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(128), nullable=True),
        sa.Column('language', sa.String(5), default='fa'),
        sa.Column('role', sa.Enum('user', 'music_admin', 'service_admin', 'super_admin', 'owner', name='userrole'), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=True),
        sa.Column('permissions_override', sa.Text(), nullable=True),
        sa.Column('custom_commands', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('active', 'banned', 'suspended', 'pending_verification', name='userstatus'), default='active'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_banned', sa.Boolean(), default=False),
        sa.Column('ban_reason', sa.String(255), nullable=True),
        sa.Column('banned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('banned_by', sa.BigInteger(), nullable=True),
        sa.Column('wallet_balance', sa.Integer(), default=0),
        sa.Column('wallet_hold', sa.Integer(), default=0),
        sa.Column('total_spent', sa.Integer(), default=0),
        sa.Column('total_deposits', sa.Integer(), default=0),
        sa.Column('total_downloads', sa.Integer(), default=0),
        sa.Column('total_orders', sa.Integer(), default=0),
        sa.Column('total_tickets', sa.Integer(), default=0),
        sa.Column('total_referrals', sa.Integer(), default=0),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('referrer_id', sa.BigInteger(), nullable=True),
        sa.Column('referral_code', sa.String(32), unique=True, nullable=True),
        sa.Column('referral_count', sa.Integer(), default=0),
        sa.Column('referral_earnings', sa.Integer(), default=0),
        sa.Column('ai_preferences', sa.JSON(), nullable=True),
        sa.Column('favorite_genres', sa.JSON(), nullable=True),
        sa.Column('favorite_artists', sa.JSON(), nullable=True),
        sa.Column('behavior_profile', sa.JSON(), nullable=True),
        sa.Column('last_ai_interaction', sa.DateTime(timezone=True), nullable=True),
        sa.Column('login_attempts', sa.Integer(), default=0),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_token', sa.String(255), nullable=True),
        sa.Column('session_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('totp_secret', sa.String(32), nullable=True),
        sa.Column('is_2fa_enabled', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])
    op.create_index('idx_user_role_status', 'users', ['role', 'status'])

    # Tenants table
    op.create_table('tenants',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('slug', sa.String(64), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('bot_token', sa.String(255), nullable=True),
        sa.Column('bot_username', sa.String(64), nullable=True),
        sa.Column('webhook_url', sa.String(255), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('primary_color', sa.String(7), default='#0088cc'),
        sa.Column('secondary_color', sa.String(7), default='#00aaff'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_trial', sa.Boolean(), default=False),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('theme', sa.JSON(), nullable=True),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('max_users', sa.Integer(), default=10000),
        sa.Column('max_storage_gb', sa.Integer(), default=100),
        sa.Column('max_monthly_bandwidth_gb', sa.Integer(), default=1000),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])

    # Music tables
    op.create_table('music',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('artist', sa.String(200), nullable=False),
        sa.Column('album', sa.String(200), nullable=True),
        sa.Column('genre', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('duration', sa.Integer(), default=0),
        sa.Column('bitrate', sa.Integer(), default=128),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_format', sa.String(10), default='mp3'),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('cover_url', sa.String(500), nullable=True),
        sa.Column('lyrics', sa.Text(), nullable=True),
        sa.Column('plays', sa.Integer(), default=0),
        sa.Column('likes', sa.Integer(), default=0),
        sa.Column('downloads', sa.Integer(), default=0),
        sa.Column('avg_rating', sa.Float(), default=0.0),
        sa.Column('rating_count', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_featured', sa.Boolean(), default=False),
        sa.Column('is_explicit', sa.Boolean(), default=False),
        sa.Column('moderation_status', sa.String(20), default='pending'),
        sa.Column('moderation_reason', sa.String(255), nullable=True),
        sa.Column('moderated_by', sa.BigInteger(), nullable=True),
        sa.Column('moderated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('uploaded_by', sa.BigInteger(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('mood', sa.String(50), nullable=True),
        sa.Column('language', sa.String(10), default='fa'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_music_genre_active', 'music', ['genre', 'is_active'])
    op.create_index('idx_music_category_plays', 'music', ['category', 'plays'])
    op.create_index('idx_music_search_title', 'music', ['title'])
    op.create_index('idx_music_artist', 'music', ['artist'])

    # Music likes, plays, reports
    op.create_table('music_likes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('music_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['music_id'], ['music.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_music_likes_user_music', 'music_likes', ['user_id', 'music_id'], unique=True)

    op.create_table('music_plays',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('music_id', sa.Integer(), nullable=False),
        sa.Column('played_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('duration_listened', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(50), default='bot'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['music_id'], ['music.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE')
    )
    op.create_index('idx_music_plays_user_music', 'music_plays', ['user_id', 'music_id'])
    op.create_index('idx_music_plays_date', 'music_plays', ['played_at'])

    op.create_table('music_reports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('music_id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.BigInteger(), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('resolved_by', sa.BigInteger(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['music_id'], ['music.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.telegram_id'], ondelete='CASCADE')
    )

    # Services and orders
    op.create_table('services',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('slug', sa.String(64), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('vpn', 'server', 'account', 'credit', 'other', name='servicetype'), default='other'),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('compare_price', sa.Integer(), nullable=True),
        sa.Column('period', sa.Enum('monthly', 'quarterly', 'semi_annual', 'annual', 'one_time', name='serviceperiod'), default='monthly'),
        sa.Column('setup_fee', sa.Integer(), default=0),
        sa.Column('spec_data', sa.JSON(), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('stock', sa.Integer(), default=-1),
        sa.Column('delivery_type', sa.String(20), default='auto'),
        sa.Column('delivery_webhook', sa.String(255), nullable=True),
        sa.Column('delivery_data', sa.JSON(), nullable=True),
        sa.Column('max_per_user', sa.Integer(), default=1),
        sa.Column('trial_available', sa.Boolean(), default=False),
        sa.Column('trial_days', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_featured', sa.Boolean(), default=False),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_services_slug', 'services', ['slug'])

    op.create_table('orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_number', sa.String(32), unique=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('unit_price', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Integer(), nullable=False),
        sa.Column('discount', sa.Integer(), default=0),
        sa.Column('final_price', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(20), nullable=True),
        sa.Column('status', sa.Enum('pending', 'paid', 'processing', 'completed', 'cancelled', 'failed', 'refunded', 'expired', name='orderstatus'), default='pending'),
        sa.Column('payment_status', sa.Enum('unpaid', 'paid', 'refunded', 'partial', name='paymentstatus'), default='unpaid'),
        sa.Column('delivery_data', sa.JSON(), nullable=True),
        sa.Column('delivery_notes', sa.Text(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivery_attempts', sa.Integer(), default=0),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_gateway', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )
    op.create_index('ix_orders_order_number', 'orders', ['order_number'])
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])

    # Transactions
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transaction_hash', sa.String(64), unique=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('balance_before', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('deposit', 'withdrawal', 'purchase', 'refund', 'referral_bonus', 'admin_adjustment', 'service_fee', name='transactiontype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', 'cancelled', 'reversed', name='transactionstatus'), default='pending'),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('reference', sa.String(128), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('gateway', sa.String(50), nullable=True),
        sa.Column('gateway_transaction_id', sa.String(128), nullable=True),
        sa.Column('gateway_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )
    op.create_index('ix_transactions_transaction_hash', 'transactions', ['transaction_hash'])
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])

    # Tickets
    op.create_table('ticket_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(64), unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assign_to_role', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('tickets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_number', sa.String(20), unique=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('subject', sa.String(200), nullable=False),
        sa.Column('status', sa.Enum('open', 'in_progress', 'waiting_customer', 'resolved', 'closed', name='ticketstatus'), default='open'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='ticketpriority'), default='medium'),
        sa.Column('assigned_to', sa.BigInteger(), nullable=True),
        sa.Column('closed_by', sa.BigInteger(), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['ticket_categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )
    op.create_index('ix_tickets_ticket_number', 'tickets', ['ticket_number'])
    op.create_index('ix_tickets_user_id', 'tickets', ['user_id'])

    op.create_table('ticket_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )

    # Payment requests
    op.create_table('payment_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('method', sa.String(50), nullable=False),
        sa.Column('receipt_image', sa.String(500), nullable=True),
        sa.Column('transaction_id', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'expired', name='paymentrequeststatus'), default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.BigInteger(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expired_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )

    # Plugins
    op.create_table('plugins',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(64), unique=True, nullable=False),
        sa.Column('display_name', sa.String(128), nullable=False),
        sa.Column('version', sa.String(32), nullable=False),
        sa.Column('author', sa.String(128), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), default='installed'),
        sa.Column('entry_point', sa.String(255), nullable=False),
        sa.Column('config_schema', sa.JSON(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('permissions_required', sa.JSON(), nullable=True),
        sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('enabled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('plugin_installations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('installed_by', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(32), nullable=False),
        sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], )
    )

    # Audit logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])

    # System settings
    op.create_table('system_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(128), unique=True, nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(20), default='string'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_system_settings_key', 'system_settings', ['key'])

    # Menu items
    op.create_table('menu_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('command', sa.String(50), nullable=True),
        sa.Column('callback_data', sa.String(100), nullable=True),
        sa.Column('url', sa.String(255), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('role_required', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('condition', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow definitions
    op.create_table('workflow_definitions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('trigger_type', sa.String(50), nullable=False),
        sa.Column('trigger_config', sa.JSON(), nullable=True),
        sa.Column('nodes', sa.JSON(), nullable=False),
        sa.Column('edges', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # AI memory
    op.create_table('ai_memories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('memory_type', sa.String(20), default='short_term'),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), default=1.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE')
    )

    op.create_table('ai_interactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('user_message', sa.Text(), nullable=False),
        sa.Column('ai_response', sa.Text(), nullable=True),
        sa.Column('intent', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('feedback_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE')
    )

    # User sessions
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('session_token', sa.String(255), unique=True, nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], )
    )

    # System health
    op.create_table('system_health',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('component', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='healthy'),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('system_health')
    op.drop_table('user_sessions')
    op.drop_table('ai_interactions')
    op.drop_table('ai_memories')
    op.drop_table('workflow_definitions')
    op.drop_table('menu_items')
    op.drop_table('system_settings')
    op.drop_table('audit_logs')
    op.drop_table('plugin_installations')
    op.drop_table('plugins')
    op.drop_table('payment_requests')
    op.drop_table('ticket_messages')
    op.drop_table('tickets')
    op.drop_table('ticket_categories')
    op.drop_table('transactions')
    op.drop_table('orders')
    op.drop_table('services')
    op.drop_table('music_reports')
    op.drop_table('music_plays')
    op.drop_table('music_likes')
    op.drop_table('music')
    op.drop_table('tenants')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS servicetype')
    op.execute('DROP TYPE IF EXISTS serviceperiod')
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS transactionstatus')
    op.execute('DROP TYPE IF EXISTS ticketstatus')
    op.execute('DROP TYPE IF EXISTS ticketpriority')
    op.execute('DROP TYPE IF EXISTS paymentrequeststatus')
