# cmftest-begin: test_complicated_boolean
set(matchme
    "_DATA_\\|_CMAKE_\\|INTRA_PRED\\|_COMPILED\\|_HOSTING\\|_PERF_\\|CODER_")
if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
   OR (CONFIG_AV1_ENCODER
       AND CONFIG_ENCODE_PERF_TESTS
       AND "${var}" MATCHES "_ENCODE_PERF_TEST_")
   OR (CONFIG_AV1_DECODER
       AND CONFIG_DECODE_PERF_TESTS
       AND "${var}" MATCHES "_DECODE_PERF_TEST_")
   OR (CONFIG_AV1_ENCODER AND "${var}" MATCHES "_TEST_ENCODER_")
   OR (CONFIG_AV1_DECODER AND "${var}" MATCHES "_TEST_DECODER_"))
  list(APPEND aom_test_source_vars ${var})
endif()
# cmftest-end

# cmftest-begin: test_less_complicated_boolean
set(matchme
    "_DATA_\\|_CMAKE_\\|INTRA_PRED\\|_COMPILED\\|_HOSTING\\|_PERF_\\|CODER_")
if(("${var}" MATCHES "_TEST_" AND NOT "${var}" MATCHES "${matchme}")
   OR (CONFIG_AV1_ENCODER
       AND CONFIG_ENCODE_PERF_TESTS
       AND "${var}" MATCHES "_ENCODE_PERF_TEST_"))
  list(APPEND aom_test_source_vars ${var})
endif()
# cmftest-end

# cmftest-begin: test_nested_parens
if((NOT HELLO) OR (NOT EXISTS ${WORLD}))
  message(WARNING "something is wrong")
  set(foobar FALSE)
endif()
# cmftest-end

# cmftest-begin: test_negated_single_nested_parens
if(NOT ("" STREQUALS ""))
  # pass
endif()
# cmftest-end

# cmftest-begin: test_conditional_in_if_and_endif
if(SOMETHING AND (NOT SOMETHING_ELSE STREQUAL ""))
  # pass
endif(SOMETHING AND (NOT SOMETHING_ELSE STREQUAL ""))
# cmftest-end
