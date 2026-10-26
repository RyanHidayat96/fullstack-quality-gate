# frozen_string_literal: true
# Isolated database-backed specs: NEVER run against a shared/prod database.
ENV['RAILS_ENV'] = 'test'
require File.expand_path('../config/environment', __dir__)
require 'rspec/rails'

abort 'Refusing to run specs outside Rails test environment' unless Rails.env.test?

RSpec.configure do |config|
  config.use_transactional_fixtures = true
  config.infer_spec_type_from_file_location!
  config.filter_run_when_matching :focus
  config.before(:each) { RequestStore.clear! }
  config.after(:each) { RequestStore.clear! }
end
require_relative 'support/synthetic_records'
