# frozen_string_literal: true
require 'rails_helper'

RSpec.describe FitGap::Engine do
  # FITGAP-04: separate vacancy rows with equal labels cannot silently collapse.
  it 'FITGAP-04 retains each persisted vacancy skill and its distinct ID' do
    portfolio = synthetic_portfolio
    vacancy = synthetic_vacancy
    vacancy.vacancy_skills.create!(skill_id: 'skill-1', skill_label: 'Systems', expected_level: 3)
    vacancy.vacancy_skills.create!(skill_id: 'skill-2', skill_label: 'Systems', expected_level: 4)

    engine = described_class.new(portfolio: portfolio, vacancy: vacancy, gemini_client: double('unused AI'))
    rows = engine.send(:build_skill_comparisons)

    expect(rows.length).to eq(2)
    expect(rows.pluck(:skill_id)).to contain_exactly('skill-1', 'skill-2')
    expect(rows.pluck(:expected_level)).to contain_exactly(3, 4)
    expect(rows.pluck(:result)).to contain_exactly('not_assessed', 'not_assessed')
  end
end
