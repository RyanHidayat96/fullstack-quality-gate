# frozen_string_literal: true
require 'rails_helper'

RSpec.describe 'Tenant-scoped authentication', type: :request do
  let(:password) { 'test-only-password' }
  let!(:admin) { User.create!(email: 'admin@example.invalid', password: password, role: 'admin') }
  let!(:home) { Organization.create!(name: 'Home', scheme: 'home-tenant', identifier: 'home-tenant', host: 'home.example.invalid') }
  let!(:other) { Organization.create!(name: 'Other', scheme: 'other-tenant', identifier: 'other-tenant', host: 'other.example.invalid') }

  def login_as(scheme = nil)
    headers = scheme ? { 'X-Tenant-Scheme' => scheme } : {}
    post '/api/v1/auth/login', params: { email: admin.email, password: password }, headers: headers
  end

  it 'AUTH-TENANT-04 refuses tokens for tenants without membership' do
    login_as(other.scheme)
    expect(response).to have_http_status(:forbidden)
    expect(response.parsed_body).not_to have_key('token')
  end

  it 'AUTH-TENANT-05 allows a member of the selected tenant only' do
    TenantMembership.create!(user: admin, organization: home)
    login_as(home.scheme)
    expect(response).to have_http_status(:ok)
    claims = JsonWebToken.decode(response.parsed_body.fetch('token'))
    expect(claims[:scheme]).to eq(home.scheme)
  end

  it 'AUTH-TENANT-06 denies unrecognized tenant selection' do
    TenantMembership.create!(user: admin, organization: home)
    login_as('unrecognized-tenant')
    expect(response).to have_http_status(:forbidden)
  end

  it 'denies an ambiguous login without a selected tenant' do
    TenantMembership.create!(user: admin, organization: home)
    TenantMembership.create!(user: admin, organization: other)
    login_as
    expect(response).to have_http_status(:unprocessable_entity)
  end
end
