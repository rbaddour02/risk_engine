"""
Generate corrected delta summary with HTT Rolls mapping fixed
"""

import pandas as pd
from position_expander import expand_positions, create_delta_summary

# Expand positions
delta_positions_df = expand_positions('pos_summary.csv')

# Create summary table
delta_summary_df = create_delta_summary(delta_positions_df)

# Save with updated names (replacing old ones when you close the file in IDE)
delta_summary_df.to_csv('delta_summary_updated.csv')
delta_positions_df.to_csv('delta_positions_updated.csv', index=False)

print("="*100)
print("CORRECTED DELTA SUMMARY TABLE (HTT Rolls now mapped to HTT)")
print("="*100)
print()
print(delta_summary_df.to_string())
print()
print("="*100)
print("Summary by Product:")
for col in delta_summary_df.columns:
    total = delta_summary_df[col].sum()
    print("  {:10s}: {:12.2f}".format(col, total))
print("  {:10s}: {:12.2f}".format('TOTAL', delta_summary_df.values.sum()))
print()
print("Files saved:")
print("  - delta_summary_updated.csv")
print("  - delta_positions_updated.csv")
print()
print("Note: Close delta_summary.csv in your IDE to replace it with the updated version")
