# frozen_string_literal: true

# Re-check signed token claims against persisted access grants.
# This also invalidates previously issued cross-tenant tokens after rollout.
class TenantAccess
  def self.permitted?(claims)
    user = User.find_by(id: claims[:user_id])
    return false unless user && user.role == claims[:role].to_s

    tenant = Organization.find_by(scheme: claims[:scheme].to_s)
    return false unless tenant

    TenantMembership.exists?(user_id: user.id, tenant_id: tenant.id)
  end
end
