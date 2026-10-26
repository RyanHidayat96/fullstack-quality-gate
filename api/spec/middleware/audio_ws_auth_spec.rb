# frozen_string_literal: true
require 'rails_helper'

RSpec.describe AudioWebSocketMiddleware do
  def audio_env(id, token)
    Rack::MockRequest.env_for("/ws/sessions/#{id}/audio",
                              'HTTP_AUTHORIZATION' => "Bearer #{token}")
  end

  it 'WS-AUTH-04 rejects a signed admin token without an authorized tenant grant' do
    org = Organization.create!(name: 'Audio Tenant', scheme: 'audio-test', identifier: 'audio-test', host: 'audio.example.invalid')
    admin = User.create!(email: 'audio-admin@example.invalid', password: 'test-only-password', role: 'admin')
    session = synthetic_session(tenant_id: org.id)
    token = JsonWebToken.encode(user_id: admin.id, role: 'admin', scheme: org.scheme)

    resolved, error = described_class.allocate.send(:authenticate_and_load, audio_env(session.id, token), session.id.to_s)
    expect(resolved).to be_nil
    expect(error).to include('Tenant membership required')
  end

  it 'accepts an authorized admin token for a tenant-owned interview session' do
    org = Organization.create!(name: 'Authorized Audio', scheme: 'audio-allowed', identifier: 'audio-allowed', host: 'allowed.example.invalid')
    admin = User.create!(email: 'audio-member@example.invalid', password: 'test-only-password', role: 'admin')
    TenantMembership.create!(user: admin, organization: org)
    session = synthetic_session(tenant_id: org.id)
    token = JsonWebToken.encode(user_id: admin.id, role: 'admin', scheme: org.scheme)

    resolved, error = described_class.allocate.send(:authenticate_and_load, audio_env(session.id, token), session.id.to_s)
    expect(error).to be_nil
    expect(resolved.id).to eq(session.id)
  end
  it 'INVITE-04 rejects an expired candidate invitation on the audio token path' do
    session = synthetic_session
    session.update!(invite_expires_at: 1.minute.ago)
    env = Rack::MockRequest.env_for("/ws/sessions/#{session.id}/audio?token=#{session.invite_token}")

    resolved, error = described_class.allocate.send(:authenticate_and_load, env, session.id.to_s)
    expect(resolved).to be_nil
    expect(error).to include('expired or revoked')
  end

end
