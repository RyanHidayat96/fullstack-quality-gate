# frozen_string_literal: true

class Vacancy < ApplicationRecord
  include TenantScoped

  has_many :vacancy_skills, dependent: :destroy
  has_many :fit_gap_reports, dependent: :destroy

  validates :role_title, presence: true

  accepts_nested_attributes_for :vacancy_skills,
                                 allow_destroy: true,
                                 reject_if: :all_blank

  # Hash the business inputs, not timestamps: detects nested skill edits and
  # in-flight background-job races without relying on clock precision.
  def fit_gap_fingerprint
    require 'digest'
    Digest::SHA256.hexdigest([
      role_title, culture_dimensions, competency_expectations,
      vacancy_skills.order(:id).pluck(:id, :skill_id, :skill_label, :expected_level)
    ].to_json)
  end
end
