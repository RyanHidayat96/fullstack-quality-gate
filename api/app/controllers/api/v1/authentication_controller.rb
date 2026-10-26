# frozen_string_literal: true

module Api
  module V1
    class AuthenticationController < ApiController
      skip_before_action :require_tenant!

      # POST /api/v1/auth/login
      def authenticate
        user = User.find_by(email: params[:email].to_s.downcase)

        return json_error('Invalid email or password', :unauthorized) unless user&.authenticate(params[:password])
        return json_error('Invalid email or password', :unauthorized) unless user.role == 'admin'

        memberships = user.tenant_memberships.includes(:organization).to_a
        requested_scheme = request.headers['X-Tenant-Scheme'].presence || params[:tenant_scheme].presence

        if requested_scheme.present?
          membership = memberships.find { |grant| grant.organization.scheme == requested_scheme }
          return json_error('Tenant access denied', :forbidden) unless membership
        elsif memberships.one?
          membership = memberships.first
        elsif memberships.empty?
          return json_error('Tenant access denied', :forbidden)
        else
          return json_error('Tenant scheme is required for multi-tenant accounts', :unprocessable_entity)
        end

        scheme = membership.organization.scheme
        token = JsonWebToken.encode({ user_id: user.id, role: user.role, scheme: scheme })

        json_response({ token: token, user: { id: user.id, email: user.email, role: user.role } })
      end
    end
  end
end
