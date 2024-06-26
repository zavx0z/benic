"""init

Revision ID: afb82946d826
Revises: 
Create Date: 2023-04-14 13:39:52.479826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afb82946d826'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('app_resource',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provider_name'), 'provider', ['name'], unique=False)
    op.create_table('server_resource',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('server_type', sa.Enum('ENVIRONMENT', 'DATABASE', 'APPLICATION', name='servertype'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_server_resource_name'), 'server_resource', ['name'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=True),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('role', sa.Enum('client', 'developer', 'bot', 'moderator', 'admin', 'superuser', name='role'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('device',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_mobile', sa.Boolean(), nullable=False),
    sa.Column('is_tablet', sa.Boolean(), nullable=False),
    sa.Column('is_browser', sa.Boolean(), nullable=False),
    sa.Column('vendor', sa.String(length=50), nullable=True),
    sa.Column('model', sa.String(length=50), nullable=True),
    sa.Column('os', sa.String(length=50), nullable=True),
    sa.Column('os_version', sa.String(length=50), nullable=True),
    sa.Column('user_agent', sa.String(length=256), nullable=True),
    sa.Column('is_connected', sa.Boolean(), nullable=True),
    sa.Column('notification_token', sa.String(length=256), nullable=True),
    sa.Column('ip', sa.String(length=50), nullable=True),
    sa.Column('tz', sa.String(length=50), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('resolution', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dialog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provider_server_association',
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('server_resource_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ),
    sa.ForeignKeyConstraint(['server_resource_id'], ['server_resource.id'], ),
    sa.PrimaryKeyConstraint('provider_id', 'server_resource_id')
    )
    op.create_table('server',
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('server_type', sa.Enum('ENVIRONMENT', 'DATABASE', 'APPLICATION', name='servertype'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ),
    sa.PrimaryKeyConstraint('provider_id', 'id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_server_name'), 'server', ['name'], unique=False)
    op.create_table('task',
    sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'COMPLETED', 'CANCELED', name='taskstatus'), nullable=False),
    sa.Column('app_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_id'), 'task', ['id'], unique=False)
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    op.create_table('task_resource',
    sa.Column('app_resource_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['app_resource_id'], ['app_resource.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_resource_id'), 'task_resource', ['id'], unique=False)
    op.create_index(op.f('ix_task_resource_name'), 'task_resource', ['name'], unique=False)
    op.create_table('workspace',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_modified_date', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dialog_participant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('dialog_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['dialog_id'], ['dialog.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=1000), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('dialog_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['dialog_id'], ['dialog.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('server_app_association',
    sa.Column('server_id', sa.Integer(), nullable=False),
    sa.Column('app_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.PrimaryKeyConstraint('server_id', 'app_id')
    )
    op.create_table('workspace_server_association',
    sa.Column('workspace_id', sa.Integer(), nullable=False),
    sa.Column('server_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
    sa.PrimaryKeyConstraint('workspace_id', 'server_id')
    )
    op.create_table('workspace_user_association',
    sa.Column('workspace_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
    sa.PrimaryKeyConstraint('workspace_id', 'user_id')
    )
    op.create_table('message_readers',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('read_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('message_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_readers')
    op.drop_table('workspace_user_association')
    op.drop_table('workspace_server_association')
    op.drop_table('server_app_association')
    op.drop_table('message')
    op.drop_table('dialog_participant')
    op.drop_table('workspace')
    op.drop_index(op.f('ix_task_resource_name'), table_name='task_resource')
    op.drop_index(op.f('ix_task_resource_id'), table_name='task_resource')
    op.drop_table('task_resource')
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_index(op.f('ix_task_id'), table_name='task')
    op.drop_table('task')
    op.drop_index(op.f('ix_server_name'), table_name='server')
    op.drop_table('server')
    op.drop_table('provider_server_association')
    op.drop_table('dialog')
    op.drop_table('device')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_server_resource_name'), table_name='server_resource')
    op.drop_table('server_resource')
    op.drop_index(op.f('ix_provider_name'), table_name='provider')
    op.drop_table('provider')
    op.drop_table('app_resource')
    op.drop_table('app')
    # ### end Alembic commands ###
