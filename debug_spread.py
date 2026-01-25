"""
Debug the Q2-26/Q3-26 spread expansion
"""

from position_expander import build_tenor_mappings, expand_spread, expand_positions
import pandas as pd

quarterly_map, half_year_map, calendar_map = build_tenor_mappings()

print("Testing expand_spread directly:")
result = expand_spread('Q2-26/Q3-26', -1400, quarterly_map, half_year_map, calendar_map)
print("expand_spread('Q2-26/Q3-26', -1400) returns:")
for qty, tenor in result:
    print("  {}: {}".format(tenor, qty))

print("\nNow checking what's in delta_positions:")
delta_df = pd.read_csv('delta_positions.csv')
htt_rolls_q2q3 = delta_df[(delta_df['Product'] == 'HTT Rolls') & 
                          (delta_df['Tenor'].isin(['J6', 'K6', 'M6', 'N6', 'Q6', 'U6']))]
print("Rows for J6, K6, M6, N6, Q6, U6 in HTT Rolls:")
print(htt_rolls_q2q3[['Qty', 'Tenor', 'Product']].to_string())

print("\nLet's expand manually:")
delta_all = expand_positions('pos_summary.csv')
htt_rolls_q2q3_expanded = delta_all[(delta_all['Product'] == 'HTT Rolls') & 
                                    (delta_all['Tenor'].isin(['J6', 'K6', 'M6', 'N6', 'Q6', 'U6']))]
print("Rows for J6, K6, M6, N6, Q6, U6 in expanded positions:")
print(htt_rolls_q2q3_expanded[['Qty', 'Tenor', 'Product']].to_string())
