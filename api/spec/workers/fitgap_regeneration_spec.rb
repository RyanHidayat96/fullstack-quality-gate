# frozen_string_literal: true
require 'rails_helper'

RSpec.describe 'Fit/gap worker and source freshness', type: :service do
  it 'FITGAP-03 refuses to commit results built against a superseded vacancy version' do
    session = synthetic_session(tenant_id: 12_001)
    portfolio = synthetic_portfolio(session: session)
    vacancy = synthetic_vacancy(tenant_id: session.tenant_id)
    required_skill = vacancy.vacancy_skills.create!(
      skill_id: 'design-01', skill_label: 'System Design', expected_level: 3
    )

    # Simulate an authorized edit while an asynchronous narrative request is in flight.
    ai = double('Narrative client')
    allow(ai).to receive(:generate_content) do
      required_skill.update!(expected_level: 4)
      { 'culture_narrative' => 'Synthetic result', 'overall_narrative' => 'Synthetic result' }
    end

    expect do
      FitGap::Engine.new(portfolio: portfolio, vacancy: vacancy, gemini_client: ai).call
    end.to raise_error(FitGap::StaleSourceError)

    expect(FitGapReport.where(portfolio_id: portfolio.id, vacancy_id: vacancy.id)).to be_empty
    expect(required_skill.reload.expected_level).to eq(4)
  end
end
