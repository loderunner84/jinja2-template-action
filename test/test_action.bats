#!/usr/bin/env bats

setup() {
    load 'test_helper/bats-assert/load'
    load 'test_helper/bats-file/load'
}

@test "action result" {
  assert_file_not_exist test/template.j2
  assert_file_exist test/template
  content=$(cat test/template)
  assert_equal $content 'integ'
}
