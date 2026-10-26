# frozen_string_literal: true
# Synthetic account and assessment for an isolated CI database only.
require 'json'
require 'tmpdir'
abort 'Browser E2E fixtures must never target a non-test environment' unless Rails.env.test?

scheme = 'e2e-isolated'
org = Organization.find_or_create_by!(scheme: scheme) do |record|
  record.name = 'Synthetic E2E Organization'
  record.identifier = scheme
  record.host = 'e2e.example.invalid'
end
email = 'e2e-assessor@example.invalid'
password = 'synthetic-e2e-test-only'
admin = User.find_or_create_by!(email: email) do |record|
  record.password = password
  record.role = 'admin'
end
TenantMembership.find_or_create_by!(user: admin, organization: org)
assessment = Assessment.create!(
  tenant_id: org.id, created_by: admin.id, name: 'E2E Browser Assessment',
  time_limit_min: 30, language: 'en'
)
path = File.join(Dir.tmpdir, 'quality-net-browser-fixture.json')
File.write(path, JSON.pretty_generate(
  email: email, password: password, scheme: scheme,
  assessment_id: assessment.id
))
puts "E2E fixture ready: #{path} (no real candidate records)"
