# frozen_string_literal: true
require 'rails_helper'

RSpec.describe 'Candidate session completion', type: :request do
  it 'SESSION-01 rejects pending invite without changing DB or enqueuing a job' do
    session = synthetic_session
    allow(PortfolioGeneratorWorker).to receive(:perform_async)
    post "/api/v1/sessions/#{session.invite_token}/audio_complete"
    expect(response.status).to be_between(400, 499).inclusive
    expect(session.reload.status).to eq('pending')
    expect(session.portfolio).to be_nil
    expect(PortfolioGeneratorWorker).not_to have_received(:perform_async)
  end

  it 'SESSION-02 rejects active interview without the persisted WS completion signal' do
    session = synthetic_session
    session.update!(status: 'active', started_at: Time.current)
    allow(PortfolioGeneratorWorker).to receive(:perform_async)
    post "/api/v1/sessions/#{session.invite_token}/audio_complete"
    expect(response.status).to be_between(400, 499).inclusive
    expect(session.reload.status).to eq('active')
    expect(PortfolioGeneratorWorker).not_to have_received(:perform_async)
  end

  it 'SESSION-03 finishes an acknowledged covered interview exactly once' do
    session = synthetic_session
    session.update!(status: 'active', started_at: Time.current, ready_to_end_at: Time.current)
    session.coverage_maps.create!(skill_id: 's1', skill_label: 'Systems', is_discovered: false,
                                  state: 'covered', probe_count: 2)
    allow(PortfolioGeneratorWorker).to receive(:perform_async)
    2.times { post "/api/v1/sessions/#{session.invite_token}/audio_complete" }
    expect(response).to have_http_status(:ok)
    expect(session.reload.status).to eq('ended')
    expect(session.reload.end_reason).to eq('all_covered')
    expect(session.portfolio).not_to be_nil
    expect(PortfolioGeneratorWorker).to have_received(:perform_async).once
  end
end
