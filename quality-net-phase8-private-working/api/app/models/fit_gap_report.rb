# frozen_string_literal: true

class FitGapReport < ApplicationRecord
  FIT_RESULTS = %w[match gap exceed not_assessed].freeze

  belongs_to :portfolio
  belongs_to :vacancy

  validates :skill_comparisons, presence: true

  # Reports without a saved fingerprint (older rows) must never appear current.
  def stale?
    source_fingerprint.blank? || source_fingerprint != vacancy.fit_gap_fingerprint
  end
end
