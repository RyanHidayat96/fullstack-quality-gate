# frozen_string_literal: true

class AddInvitationLifecycleToSessions < ActiveRecord::Migration[7.0]
  def up
    add_column :sessions, :invite_expires_at, :datetime, precision: 6
    add_column :sessions, :invite_revoked_at, :datetime, precision: 6

    # Fail closed for existing invitations; never grandfather unlimited tokens.
    execute <<~SQL
      UPDATE ai_interview.sessions
      SET invite_expires_at = created_at + INTERVAL '7 days'
      WHERE invite_expires_at IS NULL;
    SQL

    change_column_null :sessions, :invite_expires_at, false
  end

  def down
    remove_column :sessions, :invite_revoked_at
    remove_column :sessions, :invite_expires_at
  end
end
