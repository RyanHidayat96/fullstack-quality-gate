# frozen_string_literal: true
require 'rails_helper'

RSpec.describe 'Authenticated tenant API and persistence', type: :request do
  let!(:home) { Organization.create!(name: 'Tenant Home', scheme: 'api-home', identifier: 'api-home', host: 'api-home.example.invalid') }
  let!(:other) { Organization.create!(name: 'Tenant Other', scheme: 'api-other', identifier: 'api-other', host: 'api-other.example.invalid') }
  let!(:admin) { User.create!(email: 'api-reviewer@example.invalid', password: 'test-only-password', role: 'admin') }

  def auth_headers
    TenantMembership.find_or_create_by!(user: admin, organization: home)
    token = JsonWebToken.encode(user_id: admin.id, role: admin.role, scheme: home.scheme)
    { 'Authorization' => "Bearer #{token}" }
  end

  it 'AUTH-TENANT-01 hides foreign sessions and portfolio exports even when IDs are known' do
    foreign_session = synthetic_session(tenant_id: other.id)
    foreign_portfolio = synthetic_portfolio(session: foreign_session)

    get "/api/v1/sessions/#{foreign_session.id}", headers: auth_headers
    expect(response).to have_http_status(:not_found)

    get "/api/v1/portfolios/#{foreign_portfolio.id}/export", headers: auth_headers
    expect(response).to have_http_status(:not_found)
    expect(response.body).not_to include('Synthetic Candidate')
  end

  it 'AUTH-TENANT-02 refuses foreign portfolio overrides without database changes' do
    foreign_session = synthetic_session(tenant_id: other.id)
    portfolio = synthetic_portfolio(session: foreign_session)
    skill = portfolio.portfolio_skills.create!(
      skill_id: 'review-skill', skill_label: 'Systems', ai_level: 3,
      ai_confidence: 'medium', evidence: [], competency_summary: 'Synthetic evidence'
    )

    post "/api/v1/portfolio_skills/#{skill.id}/override",
         params: { override: { override_level: 5, assessor_notes: 'Unapproved override' } },
         headers: auth_headers

    expect(response).to have_http_status(:not_found)
    expect(skill.reload.assessor_override).to be_nil
  end

  it 'INVITE-02 persists a new assessment and a candidate invitation across HTTP requests' do
    allow(SystemPromptGeneratorWorker).to receive(:perform_async)
    post '/api/v1/assessments',
         params: { assessment: { name: 'Synthetic Design Review', time_limit_min: 30, language: 'en' } },
         headers: auth_headers
    expect(response).to have_http_status(:created)

    assessment_id = response.parsed_body.fetch('assessment').fetch('id')
    assessment = Assessment.unscoped.find(assessment_id)
    expect(assessment.tenant_id).to eq(home.id)
    expect(assessment.name).to eq('Synthetic Design Review')

    post "/api/v1/assessments/#{assessment_id}/sessions",
         params: { session: { candidate_name: 'Synthetic Guest' } },
         headers: auth_headers
    expect(response).to have_http_status(:created)
    body = response.parsed_body
    invite_url = body.fetch('invite_url')
    session = Session.unscoped.find(body.fetch('session').fetch('id'))
    expect(session.tenant_id).to eq(home.id)
    expect(invite_url).to include("/interview/#{session.invite_token}")

    get "/api/v1/sessions/#{session.invite_token}/candidate"
    expect(response).to have_http_status(:ok)
    expect(response.parsed_body.fetch('role_title')).to eq('Synthetic Design Review')
    expect(response.parsed_body.fetch('session_status')).to eq('pending')
  end
end
