#!/usr/bin/env bats

setup() {
  load 'test_helper/bats-support/load'
  load 'test_helper/bats-assert/load'
  load 'test_helper/bats-file/load'
}

@test "Test Action with all possible entries" {
  assert_file_not_exist all_test.j2
  assert_file_exist all_test
  run -0 cmp -s all_test expected
}
