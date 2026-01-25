from position_expander import expand_spread, build_tenor_mappings

quarterly_map, half_year_map, calendar_map = build_tenor_mappings()

result = expand_spread('J6/Q2-26', -120, quarterly_map, half_year_map, calendar_map)

print('expand_spread("J6/Q2-26", -120) returns:')
for qty, tenor in sorted(result, key=lambda x: x[1]):
    print('  {}: {}'.format(tenor, qty))
print()
print('Expected:')
print('  J6: -120 (first leg, 1 tenor)')
print('  K6: +40 (second leg, Q2-26 has 3 tenors, so 120/3 = 40)')
print('  M6: +40')
print('  N6: +40')
