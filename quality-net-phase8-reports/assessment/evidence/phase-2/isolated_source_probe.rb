# frozen_string_literal: true
# Audit-only isolated source probe; no Rails, DB, HTTP, external credentials, or source changes.
# Run: ruby assessment/evidence/phase-2/isolated_source_probe.rb
require 'json'
require 'pathname'
ROOT = Pathname.new(__dir__).join('../../..').realpath
results = []

def record(results, id, actual, expected, evidence)
  results << { id: id, actual: actual, expected: expected, demonstrates_risk: actual != expected, evidence: evidence }
end

# Exercise actual private method from application source against minimal immutable stubs.
class Array
  def index_by
    each_with_object({}) { |value, result| result[yield(value)] = value }
  end
end
module FitGap; end
load ROOT.join('api/app/services/fit_gap/engine.rb')
Skill = Struct.new(:skill_label, :skill_id, :expected_level)
Vacancy = Struct.new(:vacancy_skills)
engine = FitGap::Engine.allocate
engine.instance_variable_set(:@vacancy, Vacancy.new([Skill.new('Cloud Design', 'SK01', 2), Skill.new('Cloud Design', 'SK02', 4)]))
def engine.effective_portfolio_skills; []; end
comparisons = engine.send(:build_skill_comparisons)
record(results, 'FIND-003', comparisons.size, 2,
       'actual FitGap::Engine#build_skill_comparisons; two vacancy skill rows sharing a label produce one comparison')

# Execute actual production SessionsController#audio_complete method on a fake repository.
module Api
  module V1
    class ApiController
      def self.authorize_auth_token!(*); end
      def self.skip_before_action(*); end
      def self.before_action(*); end
      def params; { token: 'synthetic-invite-token' }; end
      def json_response(result, *_args); result; end
      def json_error(message, *_args); { error: message }; end
    end
  end
end
FakeSession = Struct.new(:status) do
  def ended?; status == 'ended'; end
end
class Session
  def self.unscoped; self; end
  def self.find_by(invite_token:); FakeSession.new('pending'); end
end
module Sessions
  class EndHandler
    @@recorded_reasons = []
    def self.recorded_reasons; @@recorded_reasons; end
    def initialize(session); @session = session; end
    def call(reason:); @@recorded_reasons << { status_before: @session.status, reason: reason }; true; end
  end
end
load ROOT.join('api/app/controllers/api/v1/sessions_controller.rb')
response = Api::V1::SessionsController.new.audio_complete
actual = { response: response, end_calls: Sessions::EndHandler.recorded_reasons }
record(results, 'FIND-002', actual,
       { response: { error: 'Session not ready to complete' }, end_calls: [] },
       'actual SessionsController#audio_complete; valid invite token on pending session invokes EndHandler(all_covered) and responds ended=true')

# Exercise exactly the expression used to persist AI model skill ratings.
raw = ['n/a', nil, -2, 88, '4']
actual = raw.map { |v| { input: v, persisted: v.to_i.clamp(1, 5) } }
record(results, 'FIND-005', actual,
       raw.map { |v| { input: v, persisted: (v == '4' ? 4 : :rejected) } },
       "api/app/services/portfolios/generator.rb:161,173; literal production normalization expression")

# Validate URL generation using the actual production Session#invite_url method.
module TenantScoped; end
class ApplicationRecord
  def self.belongs_to(*); end
  def self.has_many(*); end
  def self.has_one(*); end
  def self.validates(*); end
  def self.before_validation(*); end
  def self.scope(*); end
end
# Session model is defined already; replace fake class with real model without altering disk source.
Object.send(:remove_const, :Session)
load ROOT.join('api/app/models/session.rb')
model = Session.allocate
def model.invite_token; 'synthetic-token'; end
url = model.invite_url
record(results, 'FIND-006', url, 'http://localhost:5173/interview/synthetic-token',
       'actual Session#invite_url under default APP_BASE_URL; documented frontend on port 5173')

puts JSON.pretty_generate({ runtime: RUBY_VERSION, framework_booted: false,
  test_type: 'isolated source probes using doubles (not Rails/DB/E2E integration tests)', probes: results })
