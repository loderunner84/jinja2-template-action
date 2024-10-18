#!/usr/bin/env bats

setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'
    load 'test_helper/bats-file/load'
}

@test "environement variable" {
  assert_file_not_exist test/env-var/template.j2
  assert_file_exist test/env-var/template
  run -0 cmp -s test/env-var/template test/env-var/result 
}

@test "input variables" {
  assert_file_not_exist test/many-var/template.j2
  assert_file_exist test/many-var/template
  run -0 cmp -s test/many-var/template test/many-var/result 
}
