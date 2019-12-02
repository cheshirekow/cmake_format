# test: standard_form
foreach(
  loopvar
  FOO
  BAR
  BAZ
  A
  B
  C
  D)
  # pass
endforeach()

# test: range_form_1arg
foreach(loopvar RANGE 3)
  # pass
endforeach()

# test: range_form_2arg
foreach(loopvar RANGE 3 4)
  # pass
endforeach()

# test: range_form_3arg
foreach(loopvar RANGE 3 4 1)
  # pass
endforeach()

# test: in_form
foreach(
  loopvar IN
  LISTS A B C
  ITEMS D E F)
  # pass
endforeach()

