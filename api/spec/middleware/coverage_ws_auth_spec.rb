# frozen_string_literal: true
require 'rails_helper'

RSpec.describe CoverageWebSocketMiddleware do
  it 'WS-AUTH-01 refuses valid JWTs whose role is not assessor/admin' do
    allow(JsonWebToken).to receive(:decode).with('candidate-jwt').and_return(
      {user_id: 123, role: 'user', scheme: 'synthetic-tenant'}
    )
    expect(Organization).not_to receive(:find_by)
    session, error = described_class.allocate.send(:authenticate_assessor_by_token, 'candidate-jwt', 42)
    expect(session).to be_nil
    expect(error).to include('Assessor permission required')
  end
end
