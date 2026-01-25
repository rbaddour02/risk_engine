from position_expander import expand_tenor_structure, build_tenor_mappings

quarterly_map, half_year_map, calendar_map = build_tenor_mappings()

q2_tenors = expand_tenor_structure('Q2-26', quarterly_map, half_year_map, calendar_map)
print('Q2-26 expands to:', q2_tenors)

j6_tenors = expand_tenor_structure('J6', quarterly_map, half_year_map, calendar_map)
print('J6 expands to:', j6_tenors)
