# frozen_string_literal: true
# Independent, dependency-light regression probes executing ORIGINAL source methods.
# This is not a substitute for request + persisted DB tests; CI runs both suites.
# Run: ruby api/spec/regression/critical_contract_test.rb
require 'minitest/autorun'
require 'ostruct'
require 'json'

# Minimal, intentionally inert adapters so original Rails class definitions load.
module TenantScoped; end
module ActiveRecord; class RecordNotFound < StandardError; end; end
class ApplicationRecord
  def self.belongs_to(*); end
  def self.has_many(*); end
  def self.has_one(*); end
  def self.validates(*); end
  def self.before_validation(*); end
  def self.scope(*); end
  def self.accepts_nested_attributes_for(*); end
end
class ApiController
  def self.authorize_auth_token!(*); end
  def self.skip_before_action(*); end
  def self.before_action(*); end
  attr_accessor :params, :result_payload, :result_error
  def current_tenant_id; 20_002; end
  def json_response(payload, *_args); self.result_payload = payload; end
  def json_error(message, *_args); self.result_error = message; end
  def render(json:, status:); self.result_payload = json; end
end

class Array
  unless method_defined?(:index_by)
    def index_by
      each_with_object({}) { |item, acc| acc[yield(item)] = item }
    end
  end
end
class Object
  unless method_defined?(:present?)
    def blank?; nil? || self == false || self == ''; end
    def present?; !blank?; end
  end
end

# Production files loaded without modifying their methods/behavior.
require_relative '../../app/models/session'
require_relative '../../app/models/vacancy'
require_relative '../../app/models/fit_gap_report'
require_relative '../../app/controllers/api/v1/sessions_controller'
require_relative '../../app/controllers/api/v1/portfolios_controller'
require_relative '../../app/services/fit_gap/engine'
require_relative '../../app/services/portfolios/generator'
require_relative '../../app/services/coverage/map_injector'

# External-boundary stand-ins record effects, never send network requests.
class Session
  class << self
    attr_accessor :test_session
    def unscoped; self; end
    def find_by(**_); test_session; end
  end
end
module Sessions
  class EndHandler
    class << self; attr_accessor :calls; end
    self.calls = []
    def initialize(session); @session = session; end
    def call(reason:); self.class.calls << [@session.status, reason]; @session.status = 'ended'; end
  end
end
class Portfolio
  class << self; attr_accessor :test_portfolio; end
  class ScopedRecords
    def initialize(record); @record = record; end
    def where(sessions:); @tenant_id = sessions.fetch(:tenant_id); self; end
    def find(id)
      unless @record && @record.id == id && @record.tenant_id == @tenant_id
        raise ActiveRecord::RecordNotFound, 'Portfolio not found in current tenant'
      end
      @record
    end
  end
  def self.joins(*args); raise "Expected session join" unless args == [:session]; ScopedRecords.new(test_portfolio); end
  def self.find(*); test_portfolio; end
end
class Vacancy
  class << self; attr_accessor :test_vacancy; end
  def self.find_by(*); test_vacancy; end
end
class FitGapReport
  class << self; attr_accessor :test_report; end
  def self.find_by(*); test_report; end
end

class CriticalSourceRegressions < Minitest::Test
  def setup
    Sessions::EndHandler.calls = []
  end

  # SESSION-01: known defect. Rejected pending completion must persist nothing.
  def test_SESSION_01_pending_audio_complete_must_not_finalize
    s = Struct.new(:status) do
      def ended? = status == 'ended'
      def active? = status == 'active'
      def invite_valid? = true
    end.new('pending')
    Session.test_session = s
    controller = Api::V1::SessionsController.new
    controller.params = {token: 'synthetic-token'}
    controller.audio_complete
    assert_equal 'pending', s.status, 'candidate-only signal changed pending session'
    assert_empty Sessions::EndHandler.calls, 'pending session queued termination handler'
  end

  # FITGAP-04: duplicate labels with different stable skill IDs must not silently disappear.
  def test_FITGAP_04_duplicate_label_distinct_skills_must_not_disappear
    a = Struct.new(:skill_label, :skill_id, :expected_level).new('Analysis', 'skill-a', 4)
    b = Struct.new(:skill_label, :skill_id, :expected_level).new('Analysis', 'skill-b', 2)
    vacancy = Struct.new(:vacancy_skills).new([a, b])
    engine = FitGap::Engine.new(portfolio: Object.new, vacancy: vacancy, gemini_client: Object.new)
    engine.define_singleton_method(:effective_portfolio_skills) { [] }
    rows = engine.send(:build_skill_comparisons)
    assert_equal 2, rows.length, 'two source vacancy rows must yield two report comparisons'
    assert_equal %w[skill-a skill-b], rows.map { |row| row[:skill_id] }
  end

  # PORTFOLIO-01: garbage AI data must be rejected, not turned into a valid-looking L1.
  def test_PORTFOLIO_01_unparseable_AI_level_must_not_be_persisted
    association = Object.new
    def association.destroy_all; end
    def association.create!(**kwargs); (@writes ||= []) << kwargs; end
    def association.writes; @writes || []; end
    portfolio = Struct.new(:portfolio_skills).new(association)
    generator = Portfolios::Generator.new(session: Object.new, gemini_client: Object.new)
    invalid_payload = {'configured_skills' => [{ 'skill_id' => 'skill-a', 'skill_label' => 'Analysis',
      'level' => 'not_a_level', 'confidence' => 'low', 'evidence' => [], 'competency_summary' => 'Synthetic summary'}]}
    assert_raises(ArgumentError, TypeError) { generator.send(:save_skills, portfolio, invalid_payload) }
    assert_empty association.writes, 'invalid AI payload must not commit any skill row'
  end

  # INVITE-01: documented local frontend lives on 5173, API lives on 3001.
  def test_INVITE_01_default_invite_should_route_to_frontend
    old = ENV.delete('APP_BASE_URL')
    session = Session.allocate
    session.define_singleton_method(:invite_token) { 'synthetic-token' }
    assert_equal 'http://localhost:5173/interview/synthetic-token', session.invite_url
  ensure
    ENV['APP_BASE_URL'] = old if old
  end

  # AUTH-TENANT-01: simulate tenant-B assessor reading tenant-A portfolio.
  # Isolated policy probe only; request/DB tests are needed for full proof.
  def test_AUTH_TENANT_01_direct_fitgap_must_deny_foreign_portfolio
    foreign = Struct.new(:id, :tenant_id) { def complete? = true }.new(42, 20_001)
    vacancy = Struct.new(:id).new(15)
    Portfolio.test_portfolio = foreign
    Vacancy.test_vacancy = vacancy
    FitGapReport.test_report = Struct.new(:id, :portfolio_id, :vacancy_id, :skill_comparisons, :culture_narrative, :overall_narrative, :generated_at).new(33, 42, 15, [], nil, nil, nil)
    controller = Api::V1::PortfoliosController.new
    controller.params = {id: foreign.id, fitgap: {vacancy_id: vacancy.id}}
    controller.fitgap
    assert_nil controller.result_payload, 'foreign tenant portfolio produced successful fit-gap result'
    refute_nil controller.result_error, 'foreign tenant access was not denied'
  end

  def test_SESSION_02_active_without_server_ack_is_rejected
    # Deliberately mark coverage complete, so a missing readiness guard fails
    # an assertion rather than crashing on an incomplete test double.
    map = Struct.new(:state).new('covered')
    maps = Class.new(Array) { def configured = self; def discovered = []; }.new([map])
    session = Struct.new(:status, :ready_to_end_at, :coverage_maps) do
      def ended? = status == 'ended'
      def active? = status == 'active'
      def invite_valid? = true
    end.new('active', nil, maps)
    Session.test_session = session
    controller = Api::V1::SessionsController.new
    controller.params = {token: 'synthetic-token'}
    controller.audio_complete
    assert_equal 'active', session.status
    assert_empty Sessions::EndHandler.calls
    assert_equal 'Interview is not ready to complete', controller.result_error
  end

  def test_SESSION_03_active_ready_but_incomplete_coverage_does_not_end
    map = Struct.new(:state).new('partial')
    maps = Class.new(Array) { def configured = self; def discovered = []; }.new([map])
    session = Struct.new(:status, :ready_to_end_at, :coverage_maps) do
      def ended? = status == 'ended'
      def active? = status == 'active'
      def invite_valid? = true
    end.new('active', Time.now, maps)
    Session.test_session = session
    controller = Api::V1::SessionsController.new
    controller.params = {token: 'synthetic-token'}
    controller.audio_complete
    assert_equal 'active', session.status
    assert_empty Sessions::EndHandler.calls
  end

  def test_SESSION_04_active_ready_and_covered_completes_once
    map = Struct.new(:state).new('covered')
    maps = Class.new(Array) { def configured = self; def discovered = []; }.new([map])
    session = Struct.new(:status, :ready_to_end_at, :coverage_maps) do
      def ended? = status == 'ended'
      def active? = status == 'active'
      def invite_valid? = true
    end.new('active', Time.now, maps)
    Session.test_session = session
    controller = Api::V1::SessionsController.new
    controller.params = {token: 'synthetic-token'}
    controller.audio_complete
    assert_equal 'ended', session.status
    assert_equal [['active', 'all_covered']], Sessions::EndHandler.calls
    controller.audio_complete
    assert_equal 1, Sessions::EndHandler.calls.length
  end

  def test_AUTH_TENANT_02_same_tenant_access_is_preserved
    local = Struct.new(:id, :tenant_id) { def complete? = true }.new(52, 20_002)
    vacancy = Struct.new(:id).new(14)
    Portfolio.test_portfolio = local
    Vacancy.test_vacancy = vacancy
    FitGapReport.test_report = Struct.new(:id, :portfolio_id, :vacancy_id, :skill_comparisons, :culture_narrative, :overall_narrative, :generated_at).new(31, 52, 14, [], nil, nil, nil)
    FitGapReport.test_report.define_singleton_method(:stale?) { false }
    controller = Api::V1::PortfoliosController.new
    controller.params = {id: local.id, fitgap: {vacancy_id: vacancy.id}}
    controller.fitgap
    assert_nil controller.result_error
    assert_equal 31, controller.result_payload.fetch(:report).fetch(:id)
  end

  def test_PORTFOLIO_02_level_rejects_noninteger_and_out_of_range
    generator = Portfolios::Generator.new(session: Object.new, gemini_client: Object.new)
    [nil, '3', 'n/a', -1, 0, 6, 2.5, true].each do |invalid|
      assert_raises(ArgumentError) { generator.send(:validated_ai_level!, invalid) }
    end
    (1..5).each { |valid| assert_equal valid, generator.send(:validated_ai_level!, valid) }
  end

  def test_FITGAP_05_identical_label_with_other_id_cannot_borrow_score
    a = Struct.new(:skill_label, :skill_id, :expected_level).new('Analysis', 'skill-a', 4)
    b = Struct.new(:skill_label, :skill_id, :expected_level).new('Analysis', 'skill-b', 2)
    engine = FitGap::Engine.new(portfolio: Object.new, vacancy: Struct.new(:vacancy_skills).new([a, b]), gemini_client: Object.new)
    engine.define_singleton_method(:effective_portfolio_skills) do
      [{skill_id: 'skill-a', skill_label: 'Analysis', effective_level: 4, confidence: 'high'}]
    end
    rows = engine.send(:build_skill_comparisons)
    assert_equal ['match', 'not_assessed'], rows.map { |row| row[:result] }
    assert_equal [4, nil], rows.map { |row| row[:candidate_level] }
  end

  def test_FITGAP_01_fingerprint_changes_when_expected_level_changes
    skill_rows = [[10, 's1', 'Systems', 3]]
    skills = Object.new
    skills.define_singleton_method(:order) { |_column| self }
    skills.define_singleton_method(:pluck) { |*_columns| skill_rows.map(&:dup) }
    vacancy = Vacancy.allocate
    vacancy.define_singleton_method(:role_title) { 'Engineer' }
    vacancy.define_singleton_method(:culture_dimensions) { nil }
    vacancy.define_singleton_method(:competency_expectations) { nil }
    vacancy.define_singleton_method(:vacancy_skills) { skills }
    original = vacancy.fit_gap_fingerprint
    skill_rows[0][3] = 5
    refute_equal original, vacancy.fit_gap_fingerprint
    report = FitGapReport.allocate
    report.define_singleton_method(:source_fingerprint) { original }
    report.define_singleton_method(:vacancy) { vacancy }
    assert report.stale?, 'stale report must not appear current after vacancy change'
  end

end
