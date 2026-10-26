# frozen_string_literal: true

# Explicit grant for an assessor account to use a tenant.
# Never infer a grant from a user role or request-supplied tenant scheme.
class TenantMembership < ApplicationRecord
  belongs_to :user
  belongs_to :organization, foreign_key: :tenant_id

  validates :tenant_id, uniqueness: { scope: :user_id }
end
