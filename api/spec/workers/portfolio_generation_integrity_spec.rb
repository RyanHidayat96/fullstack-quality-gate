# frozen_string_literal: true
require 'rails_helper'

RSpec.describe PortfolioGeneratorWorker do
  def invalid_ai_client
    client = double('Synthetic AI client')
    allow(client).to receive(:generate_content).and_return({
      'configured_skills' => [
        {
          'skill_id' => 'skill-a', 'skill_label' => 'Systems',
          'level' => 3, 'confidence' => 'high', 'evidence' => [],
          'competency_summary' => 'Synthetic valid evidence'
        },
        {
          'skill_id' => 'skill-b', 'skill_label' => 'API Safety',
          'level' => 'not-an-integer', 'confidence' => 'low', 'evidence' => [],
          'competency_summary' => 'Invalid synthetic input'
        }
      ]
    })
    client
  end

  it 'PORTFOLIO-03 marks failed generation and never persists partial AI results' do
    session = synthetic_session
    allow(Gemini::HttpClient).to receive(:new).and_return(invalid_ai_client)

    expect { described_class.new.perform(session.id) }.to raise_error(ArgumentError)
    portfolio = Portfolio.find_by!(session_id: session.id)
    expect(portfolio.generation_status).to eq('failed')
    expect(portfolio.generation_error).to include('AI level')
    expect(portfolio.portfolio_skills).to be_empty
    expect(described_class.sidekiq_options['retry']).to be >= 1
  end

  it 'preserves an existing valid portfolio skill when regeneration fails' do
    session = synthetic_session
    portfolio = synthetic_portfolio(session: session)
    good = portfolio.portfolio_skills.create!(
      skill_id: 'previous', skill_label: 'Existing Evidence', ai_level: 3,
      ai_confidence: 'medium', evidence: [], competency_summary: 'Old valid result'
    )
    allow(Gemini::HttpClient).to receive(:new).and_return(invalid_ai_client)

    expect { described_class.new.perform(session.id) }.to raise_error(ArgumentError)
    expect(portfolio.reload.generation_status).to eq('failed')
    expect(portfolio.portfolio_skills.pluck(:id)).to eq([good.id])
    expect(good.reload.ai_level).to eq(3)
  end
end
