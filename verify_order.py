import pandas as pd

df = pd.read_csv('delta_summary.csv', index_col='Tenor')

print('Tenor order in delta_summary.csv:')
print('='*80)
for i, tenor in enumerate(df.index, 1):
    print(f'{i:2d}. {tenor}')

print()
print('Verification - should be chronological:')
print('  Year 2026: H6(Mar), J6(Apr), K6(May), M6(Jun), N6(Jul), Q6(Aug), U6(Sep), V6(Oct), X6(Nov), Z6(Dec)')
print('  Year 2027: F7(Jan), G7(Feb), H7(Mar), J7(Apr), K7(May), M7(Jun), N7(Jul), Q7(Aug), U7(Sep), V7(Oct), X7(Nov), Z7(Dec)')
print('  Year 2028: F8(Jan), G8(Feb), H8(Mar), J8(Apr), K8(May), M8(Jun), N8(Jul), Q8(Aug), U8(Sep), V8(Oct), X8(Nov), Z8(Dec)')
