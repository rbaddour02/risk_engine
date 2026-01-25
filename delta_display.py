"""
Position Expansion Notebook Integration

This module can be integrated into the Jupyter notebook to display the delta summary.
"""

import pandas as pd
from position_expander import expand_positions, create_delta_summary


def display_delta_summary():
    """
    Load and display the delta summary table.
    """
    # Read the summary
    delta_summary_df = pd.read_csv('delta_summary.csv', index_col='Tenor')
    
    # Replace 0 values with empty strings for cleaner display
    display_df = delta_summary_df.copy()
    display_df = display_df.round(2)  # Round to 2 decimal places
    display_df = display_df.replace(0.0, '')
    
    return display_df


if __name__ == '__main__':
    print("Delta Summary Table (formatted for display)")
    print("=" * 80)
    summary = display_delta_summary()
    print(summary.to_string())
    
    print("\n\nDetailed Interpretation:")
    print("-" * 80)
    print("Rows: Futures contract tenors (e.g., H6 = March 2026)")
    print("Columns: Mapped products (HTT, HOUBR, CLBR, WDF, LH)")
    print("Values: Total net quantity for each tenor-product combination")
    print("\nEmpty cells indicate zero quantity for that tenor-product pair.")
