# frozen_string_literal: true

class AddFitGapSourceFingerprint < ActiveRecord::Migration[7.0]
  def change
    add_column :fit_gap_reports, :source_fingerprint, :string, limit: 64
  end
end
