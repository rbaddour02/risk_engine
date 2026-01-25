"""
Position Tenor Expansion Module

Expands contract tenors (quarterlies, halves, calendars, and spreads) into individual delta contracts
using futures mappings and product mappings.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

# ============================================================================
# TENOR MAPPINGS & PRODUCT MAPPINGS
# ============================================================================

def build_tenor_mappings():
    """
    Build all tenor expansion dictionaries.
    
    Returns:
    --------
    quarterly_map, half_year_map, calendar_map, futures_months
    
    Futures Month Mapping (all 12 months):
    F=Jan, G=Feb, H=March, J=April, K=May, M=June,
    N=July, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec
    """
    
    # Futures month codes in order (all 12 unique letters per year)
    # F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun,
    # N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec
    futures_sequence = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']  # 12 months per year
    
    # Build quarterly mappings for each year (CALENDAR-BASED)
    # Q1 = F, G, H (Jan, Feb, Mar)
    # Q2 = J, K, M (Apr, May, Jun)
    # Q3 = N, Q, U (Jul, Aug, Sep)
    # Q4 = V, X, Z (Oct, Nov, Dec)
    
    quarterly_map = {}
    half_year_map = {}
    calendar_map = {}
    
    # Generate for multiple years (2026-2028)
    for year_code_int in range(6, 9):  # Years 2026, 2027, 2028
        year_code = str(year_code_int)
        next_year_code = str(year_code_int + 1)
        
        # Quarterlies (CALENDAR-BASED: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)
        quarterly_map[f'Q1-2{year_code}'] = [f'F{year_code}', f'G{year_code}', f'H{year_code}']
        quarterly_map[f'Q2-2{year_code}'] = [f'J{year_code}', f'K{year_code}', f'M{year_code}']
        quarterly_map[f'Q3-2{year_code}'] = [f'N{year_code}', f'Q{year_code}', f'U{year_code}']
        quarterly_map[f'Q4-2{year_code}'] = [f'V{year_code}', f'X{year_code}', f'Z{year_code}']
        
        # Half-years (CALENDAR-BASED)
        # H1 = first 6 months = Jan-Jun = F, G, H, J, K, M
        # H2 = second 6 months = Jul-Dec = N, Q, U, V, X, Z
        half_year_map[f'H1-2{year_code}'] = [f'F{year_code}', f'G{year_code}', f'H{year_code}', 
                                              f'J{year_code}', f'K{year_code}', f'M{year_code}']
        half_year_map[f'H2-2{year_code}'] = [f'N{year_code}', f'Q{year_code}', f'U{year_code}',
                                              f'V{year_code}', f'X{year_code}', f'Z{year_code}']
        
        # Calendars (all 12 months)
        calendar_map[f'Cal2{year_code}'] = [f'F{year_code}', f'G{year_code}', f'H{year_code}', f'J{year_code}',
                                             f'K{year_code}', f'M{year_code}', f'N{year_code}', f'Q{year_code}',
                                             f'U{year_code}', f'V{year_code}', f'X{year_code}', f'Z{year_code}']
    
    return quarterly_map, half_year_map, calendar_map


def build_product_mapping():
    """
    Build product name to mapped product mapping.
    
    Returns:
    --------
    product_map : Dict[str, str]
    """
    product_map = {
        'HTT': 'HTT',
        'HOUBR_Cross': 'HOUBR',
        'HOUBR': 'HOUBR',
        'CLBR': 'CLBR',
        'HTT Rolls': 'HTT',        # Note: space, not underscore
        'HOUBR Boxes': 'HOUBR',    # Note: space, not underscore
        'CLBR Boxes': 'CLBR',      # Note: space, not underscore
        'HTTMID': 'LH',
        'WDF': 'WDF',
    }
    return product_map


# ============================================================================
# TENOR TYPE DETECTION & PARSING
# ============================================================================

def parse_tenor_type(tenor_str: str) -> str:
    """
    Detect tenor type: 'outright', 'quarterly', 'half', 'calendar', or 'spread'
    
    Parameters:
    -----------
    tenor_str : str
        Tenor string (e.g., 'H6', 'Q2-26', 'Cal27', 'Z6/Z7', 'J6/Q2-26')
    
    Returns:
    --------
    str : tenor type
    """
    if '/' in tenor_str:
        return 'spread'
    elif tenor_str.startswith('Q') and '-' in tenor_str:
        return 'quarterly'
    elif tenor_str.startswith('H') and '-' in tenor_str:
        return 'half'
    elif tenor_str.startswith('Cal'):
        return 'calendar'
    else:
        return 'outright'


# ============================================================================
# TENOR EXPANSION FUNCTIONS
# ============================================================================

def normalize_tenor(tenor_str: str) -> str:
    """
    Normalize tenor string to standard format.
    
    Handles: Q2-26 -> Q2-26, Q2-2026 -> Q2-26, Cal27 -> Cal27, Cal2027 -> Cal27, etc.
    """
    if 'Cal' in tenor_str:
        # Calendar tenor: Cal27 or Cal2027 -> Cal27
        if tenor_str.startswith('Cal'):
            # Extract year: Cal27 or Cal2027
            year_part = tenor_str[3:]  # "27" or "2027"
            if len(year_part) == 2:  # Cal27
                return tenor_str
            elif len(year_part) == 4:  # Cal2027
                return f'Cal{year_part[-2:]}'
        return tenor_str
    elif '-' in tenor_str and (tenor_str.startswith('Q') or tenor_str.startswith('H')):
        # Quarterly/Half: Q2-26 or Q2-2026 -> Q2-26
        parts = tenor_str.split('-')
        if len(parts) == 2:
            prefix = parts[0]  # Q2 or H2
            year = parts[1]  # 26 or 2026
            if len(year) == 2:  # Q2-26
                return tenor_str
            elif len(year) == 4:  # Q2-2026
                return f'{prefix}-{year[-2:]}'
        return tenor_str
    else:
        return tenor_str


def expand_tenor_structure(tenor_str: str, quarterly_map: Dict, half_year_map: Dict, 
                           calendar_map: Dict) -> List[str]:
    """
    Expand a tenor and return just the list of futures tenors (without quantities).
    
    Used internally for determining tenor count in spreads.
    
    Parameters:
    -----------
    tenor_str : str
        Tenor string (e.g., 'H6', 'Q2-26', 'Cal27')
    quarterly_map, half_year_map, calendar_map : Dict
        Tenor expansion mappings
    
    Returns:
    --------
    List[str] : [tenor1, tenor2, ...] (just the tenor strings)
    """
    tenor_type = parse_tenor_type(tenor_str)
    
    if tenor_type == 'outright':
        return [tenor_str]
    
    elif tenor_type == 'quarterly':
        normalized = normalize_tenor(tenor_str)
        if normalized in quarterly_map:
            return quarterly_map[normalized]
        else:
            return [tenor_str]
    
    elif tenor_type == 'half':
        normalized = normalize_tenor(tenor_str)
        if normalized in half_year_map:
            return half_year_map[normalized]
        else:
            return [tenor_str]
    
    elif tenor_type == 'calendar':
        normalized = normalize_tenor(tenor_str)
        if normalized in calendar_map:
            return calendar_map[normalized]
        else:
            return [tenor_str]
    
    else:
        return [tenor_str]


def expand_tenor(tenor_str: str, qty: float, quarterly_map: Dict, half_year_map: Dict, 
                 calendar_map: Dict) -> List[Tuple[float, str]]:
    """
    Expand a single tenor to list of (quantity, futures_tenor) tuples.
    
    Parameters:
    -----------
    tenor_str : str
        Tenor string (e.g., 'H6', 'Q2-26', 'Cal27')
    qty : float
        Quantity
    quarterly_map, half_year_map, calendar_map : Dict
        Tenor expansion mappings
    
    Returns:
    --------
    List[Tuple[float, str]] : [(qty, tenor), ...]
    """
    tenor_type = parse_tenor_type(tenor_str)
    
    if tenor_type == 'outright':
        return [(qty, tenor_str)]
    
    elif tenor_type == 'quarterly':
        # Normalize and build the map key: Q2-26 -> Q2-26
        normalized = normalize_tenor(tenor_str)
        # After normalize_tenor, we should have Q2-26 format
        # The keys in quarterly_map are like Q1-26, Q2-26, etc.
        if normalized in quarterly_map:
            futures_list = quarterly_map[normalized]
            # Assign full quantity to each tenor (no division)
            return [(qty, f) for f in futures_list]
        else:
            return [(qty, tenor_str)]  # Fallback
    
    elif tenor_type == 'half':
        # Normalize and build the map key: H2-26 -> H2-26
        normalized = normalize_tenor(tenor_str)
        # After normalize_tenor, we should have H2-26 format
        # The keys in half_year_map are like H1-26, H2-26, etc.
        if normalized in half_year_map:
            futures_list = half_year_map[normalized]
            # Assign full quantity to each tenor (no division)
            return [(qty, f) for f in futures_list]
        else:
            return [(qty, tenor_str)]  # Fallback
    
    elif tenor_type == 'calendar':
        # Normalize tenor name: Cal27 or Cal2027 -> Cal27
        normalized = normalize_tenor(tenor_str)
        # The keys in calendar_map are like Cal26, Cal27, etc.
        if normalized in calendar_map:
            futures_list = calendar_map[normalized]
            # Assign full quantity to each tenor (no division)
            return [(qty, f) for f in futures_list]
        else:
            return [(qty, tenor_str)]  # Fallback
    
    else:
        return [(qty, tenor_str)]


def expand_spread(spread_str: str, qty: float, quarterly_map: Dict, half_year_map: Dict,
                  calendar_map: Dict) -> List[Tuple[float, str]]:
    """
    Expand a spread intelligently based on tenor counts.
    
    Rules:
    - First leg: takes the sign of qty
    - Second leg: opposite sign (negated)
    - If both legs have same number of tenors: assign full |qty| to each tenor (no division)
    - If legs differ: divide only the leg with more tenors proportionally
    
    Examples:
    - Q2-26/Q3-26: 3 tenors each → qty to leg1, -qty to leg2 (no division per tenor)
    - J6/Q2-26: 1 vs 3 tenors → qty to J6, -qty/3 to each Q2-26 tenor
    - Cal27/Cal28: 12 vs 12 tenors → qty to leg1, -qty to leg2 (no division per tenor)
    
    Parameters:
    -----------
    spread_str : str
        Spread string (e.g., 'Z6/Z7', 'J6/Q2-26')
    qty : float
        Quantity for the spread (preserves sign)
    quarterly_map, half_year_map, calendar_map : Dict
        Tenor expansion mappings
    
    Returns:
    --------
    List[Tuple[float, str]] : [(qty, tenor), ...]
    """
    parts = spread_str.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid spread format: {spread_str}")
    
    leg1_str, leg2_str = parts
    
    # Expand tenors to get structure (no quantities yet)
    leg1_tenors = expand_tenor_structure(leg1_str, quarterly_map, half_year_map, calendar_map)
    leg2_tenors = expand_tenor_structure(leg2_str, quarterly_map, half_year_map, calendar_map)
    
    # Count tenors in each leg
    num_leg1 = len(leg1_tenors)
    num_leg2 = len(leg2_tenors)
    
    # Use absolute value for calculation, preserve sign for final quantity
    abs_qty = abs(qty)
    sign = 1 if qty >= 0 else -1
    
    if num_leg1 == num_leg2:
        # Same tenor count - no division needed
        leg1_qty_per_tenor = sign * abs_qty
        leg2_qty_per_tenor = -sign * abs_qty
    else:
        # Different tenor counts - divide the leg with more tenors
        if num_leg1 > num_leg2:
            # Leg1 has more tenors, so divide leg1
            leg1_qty_per_tenor = sign * abs_qty / num_leg1
            leg2_qty_per_tenor = -sign * abs_qty
        else:
            # Leg2 has more tenors, so divide leg2
            leg1_qty_per_tenor = sign * abs_qty
            leg2_qty_per_tenor = -sign * abs_qty / num_leg2
    
    # Build result with proper quantities and signs
    result = [(leg1_qty_per_tenor, t) for t in leg1_tenors]
    result.extend([(leg2_qty_per_tenor, t) for t in leg2_tenors])
    
    return result


# ============================================================================
# MAIN EXPANSION FUNCTION
# ============================================================================

def expand_positions(pos_summary_file: str) -> pd.DataFrame:
    """
    Read position summary and expand all tenors to individual futures contracts.
    
    Parameters:
    -----------
    pos_summary_file : str
        Path to pos_summary.csv
    
    Returns:
    --------
    delta_positions_df : pd.DataFrame
        Expanded positions with columns: Qty, Tenor, Product, Mapped_Product, Strategy
    """
    
    # Build mappings
    quarterly_map, half_year_map, calendar_map = build_tenor_mappings()
    product_map = build_product_mapping()
    
    # Load position summary
    df_pos = pd.read_csv(pos_summary_file)
    
    # List to collect all expanded rows
    expanded_rows = []
    
    # Process each position
    for idx, row in df_pos.iterrows():
        qty = row['Qty']
        tenor_str = row['Tenor']
        product_str = row['Product']
        strategy_str = row['Strategy']
        
        # Map product
        mapped_product = product_map.get(product_str, product_str)
        
        # Expand tenor
        tenor_type = parse_tenor_type(tenor_str)
        
        if tenor_type == 'spread':
            expanded = expand_spread(tenor_str, qty, quarterly_map, half_year_map, calendar_map)
        else:
            expanded = expand_tenor(tenor_str, qty, quarterly_map, half_year_map, calendar_map)
        
        # Add rows for each expanded tenor
        for exp_qty, exp_tenor in expanded:
            expanded_rows.append({
                'Qty': exp_qty,
                'Tenor': exp_tenor,
                'Product': product_str,
                'Mapped_Product': mapped_product,
                'Strategy': strategy_str
            })
    
    delta_positions_df = pd.DataFrame(expanded_rows)
    return delta_positions_df


# ============================================================================
# SUMMARY TABLE CREATION
# ============================================================================

def create_delta_summary(delta_positions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a pivot table summary: rows=tenors, columns=products, values=quantities
    
    Parameters:
    -----------
    delta_positions_df : pd.DataFrame
        Expanded positions
    
    Returns:
    --------
    summary_df : pd.DataFrame
        Pivot table with tenors as rows and products as columns
    """
    
    # Group by tenor and mapped_product, sum quantities
    grouped = delta_positions_df.groupby(['Tenor', 'Mapped_Product'])['Qty'].sum().reset_index()
    
    # Pivot: tenors as rows, products as columns
    summary_df = grouped.pivot_table(
        index='Tenor', 
        columns='Mapped_Product', 
        values='Qty',
        fill_value=0  # Fill zeros for missing combinations
    )
    
    # Define all possible products for consistent column order
    all_products = ['HTT', 'HOUBR', 'CLBR', 'WDF', 'LH']
    
    # Reorder columns to match desired order, only include columns that exist
    existing_products = [p for p in all_products if p in summary_df.columns]
    summary_df = summary_df[existing_products]
    
    # Sort tenor rows in chronological order
    # Define sort order for month codes and year codes
    # F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun,
    # N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec
    month_order = {'F': 0, 'G': 1, 'H': 2, 'J': 3, 'K': 4, 'M': 5, 
                   'N': 6, 'Q': 7, 'U': 8, 'V': 9, 'X': 10, 'Z': 11}
    
    def tenor_sort_key(tenor):
        """Extract sort key from tenor string like 'J6' or 'F7'"""
        if len(tenor) < 2:
            return (9999, 9999)  # Invalid tenors go to the end
        
        month_letter = tenor[0]
        try:
            year_code = int(tenor[1:])
            year = 2000 + year_code
            month_idx = month_order.get(month_letter, 10)
            return (year, month_idx)
        except ValueError:
            return (9999, 9999)  # Invalid year code
    
    # Create a sorted index
    sorted_tenors = sorted(summary_df.index, key=tenor_sort_key)
    summary_df = summary_df.loc[sorted_tenors]
    
    return summary_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    # Paths
    pos_summary_file = 'pos_summary.csv'
    
    # Expand positions
    print("Expanding positions from pos_summary.csv...")
    delta_positions_df = expand_positions(pos_summary_file)
    
    print("\nExpanded Delta Positions (first 30 rows):")
    print(delta_positions_df.head(30).to_string())
    
    # Create summary table
    print("\n\nCreating delta summary table...")
    delta_summary_df = create_delta_summary(delta_positions_df)
    
    print("\nDelta Summary Table (Tenors × Products):")
    print(delta_summary_df.to_string())
    
    # Save outputs
    delta_positions_df.to_csv('delta_positions.csv', index=False)
    delta_summary_df.to_csv('delta_summary.csv')
    
    print("\n\nOutputs saved:")
    print("  - delta_positions.csv (expanded positions)")
    print("  - delta_summary.csv (summary table)")
