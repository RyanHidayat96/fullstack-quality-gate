# frozen_string_literal: true
require 'rails_helper'

RSpec.describe 'Candidate invitation validity', type: :request do
  it 'INVITE-04 allows a valid invite and rejects expiration and revocation across HTTP endpoints' do
    session = synthetic_session
    get "/api/v1/sessions/#{session.invite_token}/candidate"
    expect(response).to have_http_status(:ok)

    session.update!(invite_expires_at: 1.minute.ago)
    get "/api/v1/sessions/#{session.invite_token}/candidate"
    expect(response).to have_http_status(:not_found)
    post "/api/v1/sessions/#{session.invite_token}/audio_complete"
    expect(response).to have_http_status(:not_found)

    session.update!(invite_expires_at: 1.day.from_now, invite_revoked_at: Time.current)
    get "/api/v1/sessions/#{session.invite_token}/candidate"
    expect(response).to have_http_status(:not_found)
  end

  it 'lets only a tenant-authorized assessor revoke a pending invitation' do
    org = Organization.create!(name: 'Invitation Owner', scheme: 'invitation-owner', identifier: 'invitation-owner', host: 'invitation-owner.example.invalid')
    admin = User.create!(email: 'invitation-reviewer@example.invalid', password: 'test-only-password', role: 'admin')
    TenantMembership.create!(user: admin, organization: org)
    session = synthetic_session(tenant_id: org.id)
    token = JsonWebToken.encode(user_id: admin.id, role: admin.role, scheme: org.scheme)

    post "/api/v1/sessions/#{session.id}/revoke_invite", headers: { 'Authorization' => "Bearer #{token}" }
    expect(response).to have_http_status(:ok)
    expect(session.reload.invite_revoked_at).to be_present
    expect(response.body).not_to include(session.invite_token)

    get "/api/v1/sessions/#{session.invite_token}/candidate"
    expect(response).to have_http_status(:not_found)
  end
end
