#!/usr/bin/env bats

setup() {
    load 'test_helper/bats-assert/load'
    load 'test_helper/bats-file/load'
}

@test "rename template file" {
  cp test/template.j2 test.txt.j2
  ./process_file.sh test.txt.j2
  assert_file_exist test.txt
  rm test.txt
}

@test "process template file" {
  cp test/template.j2 test.txt.j2
  export TEST=toto
  ./process_file.sh test.txt.j2
  content=$(cat test.txt)
  assert_equal $content 'toto'
  rm test.txt
}