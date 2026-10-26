# frozen_string_literal: true
require 'rails_helper'

RSpec.describe CoverageWebSocketMiddleware do
  it 'WS-AUTH-01 refuses valid JWTs whose role is not assessor/admin' do
    allow(JsonWebToken).to receive(:decode).with('candidate-jwt').and_return(
      {user_id: 123, role: 'user', scheme: 'synthetic-tenant'}
    )
    expect(Organization).not_to receive(:find_by)
    session, error = described_class.allocate.send(:authenticate_assessor_by_token, 'candidate-jwt', 42)
    expect(session).to be_nil
    expect(error).to include('Assessor permission required')
  end
  it 'WS-AUTH-02 denies an admin whose tenant grant is missing' do
    admin = User.create!(email: 'ws-admin@example.invalid', password: 'test-password', role: 'admin')
    org = Organization.create!(name: 'WS Tenant', scheme: 'ws-tenant', identifier: 'ws-tenant', host: 'ws.example.invalid')
    token = JsonWebToken.encode(user_id: admin.id, role: 'admin', scheme: org.scheme)

    session, error = described_class.allocate.send(:authenticate_assessor_by_token, token, 77)
    expect(session).to be_nil
    expect(error).to include('Tenant membership required')
  end

  it 'WS-AUTH-03 allows a tenant member to monitor only their own session' do
    admin = User.create!(email: 'ws-member@example.invalid', password: 'test-password', role: 'admin')
    org = Organization.create!(name: 'WS Home', scheme: 'ws-home', identifier: 'ws-home', host: 'home-ws.example.invalid')
    other = Organization.create!(name: 'WS Other', scheme: 'ws-other', identifier: 'ws-other', host: 'other-ws.example.invalid')
    TenantMembership.create!(user: admin, organization: org)
    own_session = synthetic_session(tenant_id: org.id)
    foreign_session = synthetic_session(tenant_id: other.id)
    token = JsonWebToken.encode(user_id: admin.id, role: 'admin', scheme: org.scheme)

    allowed_session, allowed_error = described_class.allocate.send(:authenticate_assessor_by_token, token, own_session.id)
    blocked_session, blocked_error = described_class.allocate.send(:authenticate_assessor_by_token, token, foreign_session.id)
    expect(allowed_error).to be_nil
    expect(allowed_session.id).to eq(own_session.id)
    expect(blocked_session).to be_nil
    expect(blocked_error).to include('Session not found')
  end

end
