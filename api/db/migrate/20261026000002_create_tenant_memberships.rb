# frozen_string_literal: true

class CreateTenantMemberships < ActiveRecord::Migration[7.0]
  def change
    create_table :tenant_memberships do |t|
      t.references :user, null: false, foreign_key: true
      t.bigint :tenant_id, null: false
      t.timestamps null: false
    end

    add_index :tenant_memberships, [:user_id, :tenant_id],
              unique: true, name: 'idx_tenant_memberships_user_tenant'
    add_foreign_key :tenant_memberships, 'public.organizations', column: :tenant_id
  end
end
