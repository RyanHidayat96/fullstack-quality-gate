# frozen_string_literal: true

class AddServerEndReadinessToSessions < ActiveRecord::Migration[7.0]
  def change
    add_column :sessions, :ready_to_end_at, :datetime
  end
end
