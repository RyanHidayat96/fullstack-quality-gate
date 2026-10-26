# frozen_string_literal: true
require 'rails_helper'

RSpec.describe 'Fit-gap report freshness', type: :model do
  it 'FITGAP-01 marks a formerly fresh report stale after vacancy skill edit' do
    portfolio = synthetic_portfolio
    vacancy = synthetic_vacancy
    skill = vacancy.vacancy_skills.create!(skill_id: 's1', skill_label: 'Systems', expected_level: 3)
    report = FitGapReport.create!(portfolio: portfolio, vacancy: vacancy,
                                  source_fingerprint: vacancy.fit_gap_fingerprint,
                                  skill_comparisons: [{'skill_label' => 'Systems', 'expected_level' => 3}])
    expect(report).not_to be_stale

    skill.update!(expected_level: 5)

    expect(report.reload).to be_stale
    expect(report.skill_comparisons.first.fetch('expected_level')).to eq(3) # old stored data is not trustworthy
  end

  it 'FITGAP-02 treats pre-migration reports without fingerprints as stale' do
    portfolio = synthetic_portfolio
    vacancy = synthetic_vacancy
    old_report = FitGapReport.create!(portfolio: portfolio, vacancy: vacancy,
                                      skill_comparisons: [{'skill_label' => 'Systems'}])
    expect(old_report).to be_stale
  end
end
