# frozen_string_literal: true
# Fixture data for test-only database, no real candidates/accounts.
module SyntheticRecords
  def synthetic_assessment(tenant_id: 10001)
    Assessment.create!(
      tenant_id: tenant_id,
      created_by: 999,
      name: 'Synthetic Engineering Assessment',
      time_limit_min: 30
    )
  end

  def synthetic_session(tenant_id: 10001, assessment: nil)
    assessment ||= synthetic_assessment(tenant_id: tenant_id)
    Session.create!(assessment: assessment, tenant_id: tenant_id,
                    candidate_name: 'Synthetic Candidate')
  end

  def synthetic_portfolio(session: nil)
    session ||= synthetic_session
    Portfolio.create!(session: session, generation_status: 'complete')
  end

  def synthetic_vacancy(tenant_id: 10001)
    Vacancy.create!(tenant_id: tenant_id, created_by: 999,
                    role_title: 'Synthetic Engineering Vacancy')
  end
end

RSpec.configure { |config| config.include SyntheticRecords }
