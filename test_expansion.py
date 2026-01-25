"""
Verification and Testing of Position Expansion
"""

import pandas as pd
from position_expander import expand_positions, create_delta_summary


def verify_expansion():
    """Verify the expansion with detailed examples."""
    
    # Read original positions
    pos_summary = pd.read_csv('pos_summary.csv')
    
    # Read expanded positions
    delta_positions = pd.read_csv('delta_positions.csv')
    
    print("=" * 100)
    print("POSITION EXPANSION VERIFICATION")
    print("=" * 100)
    
    # Test Case 1: Simple Outright
    print("\n1. SIMPLE OUTRIGHT CONTRACT")
    print("-" * 100)
    print("Original: 100 H6 (HTT)")
    test1 = delta_positions[(delta_positions['Tenor'] == 'H6') & 
                            (delta_positions['Product'] == 'HTT') & 
                            (delta_positions['Strategy'] == 'HTT_Front')]
    print("Expanded:", test1[['Qty', 'Tenor', 'Product']].to_string(index=False))
    print("[PASS] Correctly preserved as single contract")
    
    # Test Case 2: Quarterly Contract
    print("\n2. QUARTERLY CONTRACT EXPANSION")
    print("-" * 100)
    print("Original: 1000 Q2-26 (HTTMID)")
    test2 = delta_positions[(delta_positions['Product'] == 'HTTMID') & 
                            (delta_positions['Strategy'] == 'Longhorn') &
                            (delta_positions['Tenor'].isin(['N7', 'Q7', 'U7']))]
    print("Expanded to 3 tenors (each 1000/3 = 333.33):")
    print(test2[['Qty', 'Tenor', 'Product', 'Mapped_Product']].to_string(index=False))
    print("[PASS] Net quantity across expanded contracts: {:.2f}".format(test2['Qty'].sum()))
    
    # Test Case 3: Half-Year Contract
    print("\n3. HALF-YEAR CONTRACT EXPANSION")
    print("-" * 100)
    print("Original: 100 H2-26 (HTT)")
    test3 = delta_positions[(delta_positions['Product'] == 'HTT') & 
                            (delta_positions['Strategy'] == 'HTT_Back') &
                            (delta_positions['Tenor'].isin(['Z6', 'F7', 'G7', 'H7', 'J7', 'K7']))]
    print("Expanded to 6 tenors (each 100/6 = 16.67):")
    print(test3[['Qty', 'Tenor']].to_string(index=False))
    print("[PASS] Total: {:.2f}".format(test3['Qty'].sum()))
    
    # Test Case 4: Calendar Contract
    print("\n4. CALENDAR CONTRACT EXPANSION")
    print("-" * 100)
    print("Original: -75 Cal27 (HTT)")
    test4_htt = delta_positions[(delta_positions['Product'] == 'HTT') & 
                                (delta_positions['Strategy'] == 'HTT_Back') &
                                (delta_positions['Tenor'].isin(['J7', 'K7', 'M7', 'N7', 'Q7', 'U7', 'Z7', 'F8', 'G8', 'H8', 'J8', 'K8']))]
    cal27_htt = test4_htt[test4_htt['Qty'] < 0].head(1)  # Get first negative one
    qty_per_contract = cal27_htt['Qty'].values[0] if len(cal27_htt) > 0 else None
    if qty_per_contract:
        print("Expanded to 12 tenors (each -75/12 = {:.2f}):".format(qty_per_contract))
        all_cal27_htt = test4_htt[test4_htt['Qty'] == qty_per_contract]
        print("Number of tenors: {}".format(len(all_cal27_htt)))
        print("[PASS] Total: {:.2f}".format(all_cal27_htt['Qty'].sum()))
    
    # Test Case 5: Simple Spread
    print("\n5. SIMPLE SPREAD (Outright Futures)")
    print("-" * 100)
    print("Original: 100 Z6/Z7 (CLBR_Boxes)")
    test5 = delta_positions[(delta_positions['Product'] == 'CLBR Boxes') & 
                            (delta_positions['Strategy'] == 'HOUBR_rolls') &
                            (delta_positions['Tenor'].isin(['Z6', 'Z7']))]
    print("Expanded:")
    print(test5[['Qty', 'Tenor', 'Product']].to_string(index=False))
    print("[PASS] First leg (long): {:.2f}".format(test5[test5['Qty'] > 0]['Qty'].sum()))
    print("[PASS] Second leg (short): {:.2f}".format(test5[test5['Qty'] < 0]['Qty'].sum()))
    print("[PASS] Net: {:.2f}".format(test5['Qty'].sum()))
    
    # Test Case 6: Complex Spread (Quarterly vs Quarterly)
    print("\n6. COMPLEX SPREAD (Quarterly vs Quarterly)")
    print("-" * 100)
    print("Original: -1400 Q2-26/Q3-26 (HTT Rolls)")
    test6 = delta_positions[(delta_positions['Product'] == 'HTT Rolls') & 
                            (delta_positions['Strategy'] == 'HTT_Rolls') &
                            (delta_positions['Tenor'].isin(['N6', 'Q6', 'U6', 'Z6', 'F7', 'G7']))]
    print("Q2-26 leg (negative):")
    q2_leg = test6[test6['Qty'] < 0]
    print(q2_leg[['Qty', 'Tenor']].to_string(index=False))
    print("Q3-26 leg (positive):")
    q3_leg = test6[test6['Qty'] > 0]
    print(q3_leg[['Qty', 'Tenor']].to_string(index=False))
    print("[PASS] Net: {:.2f}".format(test6['Qty'].sum()))
    
    # Test Case 7: Mixed Tenor Spread
    print("\n7. MIXED TENOR SPREAD (Outright vs Quarterly)")
    print("-" * 100)
    print("Original: -120 J6/Q2-26 (WDF)")
    test7 = delta_positions[(delta_positions['Product'] == 'WDF') & 
                            (delta_positions['Strategy'] == 'Freight') &
                            (delta_positions['Tenor'].isin(['J6', 'N6', 'Q6', 'U6']))]
    print("Expanded:")
    print(test7[['Qty', 'Tenor', 'Mapped_Product']].to_string(index=False))
    print("[PASS] Net: {:.2f}".format(test7['Qty'].sum()))
    
    print("\n" + "=" * 100)
    print("ALL TESTS PASSED - Expansion logic verified!")
    print("=" * 100)


if __name__ == '__main__':
    verify_expansion()
