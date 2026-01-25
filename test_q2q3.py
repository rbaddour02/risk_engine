from position_expander import expand_spread, build_tenor_mappings

quarterly_map, half_year_map, calendar_map = build_tenor_mappings()

print('Test 1: -1400 Q2-26/Q3-26')
result = expand_spread('Q2-26/Q3-26', -1400, quarterly_map, half_year_map, calendar_map)
print('Returns:')
for qty, tenor in sorted(result, key=lambda x: x[1]):
    print('  {}: {}'.format(tenor, qty))
print()
print('Expected:')
print('  J6, K6, M6: -1400 each (Q2-26 leg1)')
print('  N6, Q6, U6: +1400 each (Q3-26 leg2)')
