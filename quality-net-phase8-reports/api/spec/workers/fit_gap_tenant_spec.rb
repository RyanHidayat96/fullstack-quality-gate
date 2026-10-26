# frozen_string_literal: true
require 'rails_helper'

RSpec.describe FitGapGeneratorWorker do
  it 'AUTH-TENANT-03 refuses to generate across tenant boundaries' do
    portfolio = synthetic_portfolio(session: synthetic_session(tenant_id: 11_001))
    vacancy = synthetic_vacancy(tenant_id: 22_002)
    expect(FitGap::Engine).not_to receive(:new)
    described_class.new.perform(portfolio.id, vacancy.id)
    expect(FitGapReport.where(portfolio_id: portfolio.id, vacancy_id: vacancy.id)).to be_empty
  end
end
