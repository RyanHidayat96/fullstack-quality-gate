# frozen_string_literal: true
require 'rails_helper'

RSpec.describe Portfolios::Generator do
  let(:valid_skill) do
    {'skill_id' => 's1', 'skill_label' => 'Systems', 'level' => 4, 'confidence' => 'low',
     'evidence' => ['synthetic evidence'], 'competency_summary' => 'Synthetic data'}
  end

  it 'PORTFOLIO-01 rejects malformed scores without deleting existing rows' do
    portfolio = synthetic_portfolio
    existing = portfolio.portfolio_skills.create!(skill_id: 'existing', skill_label: 'Existing',
      is_discovered: false, ai_level: 3, ai_confidence: 'low',
      evidence: [], competency_summary: 'Existing valid result')
    generator = described_class.new(session: portfolio.session, gemini_client: double('unused AI'))
    payload = {'configured_skills' => [valid_skill, valid_skill.merge('level' => 'garbage')], 'discovered_skills' => []}

    expect { generator.send(:save_skills, portfolio, payload) }.to raise_error(ArgumentError)
    expect(portfolio.portfolio_skills.reload.pluck(:id)).to eq([existing.id])
    expect(portfolio.portfolio_skills.first.ai_level).to eq(3)
  end

  it 'PORTFOLIO-02 saves a valid level unchanged' do
    portfolio = synthetic_portfolio
    generator = described_class.new(session: portfolio.session, gemini_client: double('unused AI'))
    generator.send(:save_skills, portfolio,
                   {'configured_skills' => [valid_skill], 'discovered_skills' => []})
    expect(portfolio.portfolio_skills.reload.pluck(:ai_level)).to eq([4])
  end
end
