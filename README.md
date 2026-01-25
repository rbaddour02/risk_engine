# Position Tenor Expansion System

## Project Summary

This project successfully implements a comprehensive position tenor expansion system that converts high-level trading contracts (quarterlies, halves, calendars, and spreads) into individual delta futures contracts using future mappings and product mappings.

## Quick Start

### Running the Expansion

```bash
python position_expander.py
```

This will:
1. Read `pos_summary.csv` (input positions)
2. Expand all tenors according to expansion rules
3. Generate `delta_positions.csv` (detailed expanded view)
4. Generate `delta_summary.csv` (pivot table by product)

### Verification

```bash
python test_expansion.py
```

Runs 7 comprehensive test cases covering:
- Simple outright contracts
- Quarterly expansions
- Half-year expansions
- Calendar expansions
- Simple spreads
- Complex spreads (quarterly vs quarterly)
- Mixed tenor spreads (outright vs quarterly)

## Data Quality: CME Holiday Filtering

### Critical Importance

**It is essential to filter out CME holidays from the dataset before performing any risk calculations.** This filtering is implemented in both `q_risk_report.ipynb` and `position_mc_report.ipynb`.

### Why Filter CME Holidays?

When the **CME (Chicago Mercantile Exchange) is closed but ICE (Intercontinental Exchange) is open**, the following data quality issues occur:

1. **Missing Data for CME Products**: CME-traded products (e.g., HTT) have no price data on CME holidays
2. **Available Data for ICE Products**: ICE-traded products (e.g., HOUBR, CLBR) continue to have price data
3. **Artificial Outliers**: This mismatch creates extreme outliers in the returns data when:
   - ICE products show normal price movements
   - CME products show zero or missing values
   - The next trading day shows large jumps to compensate

### Impact on Risk Calculations

These holiday-related outliers can cause:
- **Inflated covariance estimates** in EWMA calculations
- **Extremely high Marginal Contribution (MC) values** for ICE products
- **Distorted risk metrics** that don't reflect true portfolio risk
- **Unreliable Q-risk calculations**

### Implementation

Both notebooks automatically:
1. Load `holidays.csv` containing CME holiday dates
2. Filter `df_returns` to exclude all holiday dates before computing covariance matrices
3. Report how many holiday dates were removed for transparency

**Example output:**
```
Loaded 156 holiday dates from holidays.csv
Removed 156 holiday dates from returns data (out of 1040 total)
```

### Holiday File Format

The `holidays.csv` file should contain dates in `M/D/YYYY` format, one per line:
```
1/1/2022
1/17/2022
2/21/2022
...
12/25/2026
```

## Files Generated

### Output Files
1. **`delta_positions.csv`** (100 rows)
   - Detailed view with all expanded positions
   - Columns: Qty, Tenor, Product, Mapped_Product, Strategy
   - Each row is a single futures contract

2. **`delta_summary.csv`** (32 rows × 5 columns)
   - Summary pivot table
   - Rows: Futures tenors (J6 through K9)
   - Columns: Mapped products (HTT, HOUBR, CLBR, WDF, LH)
   - Values: Net quantity for each combination

### Source Code Files
1. **`position_expander.py`** - Core implementation module
2. **`delta_display.py`** - Display utilities
3. **`test_expansion.py`** - Verification tests
4. **`IMPLEMENTATION_SUMMARY.md`** - Technical documentation

## Tenor Expansion Rules

### Expansion Types Implemented

| Contract Type | Example | Expansion | Notes |
|---|---|---|---|
| Outright Futures | 100 H6 | 100 H6 | Preserved as-is |
| Quarterly | 1000 Q2-26 | 333.33 N6, 333.33 Q6, 333.33 U6 | Split evenly among 3 months |
| Half-Year | 100 H2-26 | 16.67 Z6,F7,G7,H7,J7,K7 | Split evenly among 6 months |
| Calendar | -75 Cal27 | -6.25 each of 12 tenors | Split evenly among 12 months |
| Simple Spread | 100 Z6/Z7 | 100 Z6, -100 Z7 | Long first, short second |
| Complex Spread | -1400 Q2-26/Q3-26 | Q2: -466.67×3, Q3: +466.67×3 | Balanced to net zero |
| Mixed Spread | -120 J6/Q2-26 | -120 J6, +40 N6,Q6,U6 | Balanced to net zero |

### Tenor Mapping

Futures month code sequence:
- Year 2026 (code 6): J6(Apr), K6(May), M6(Jun), N6(Jul), Q6(Aug), U6(Sep), Z6(Oct), F7(Nov), G7(Dec), H7(Jan)...
- Year 2027 (code 7): J7(Apr), K7(May), M7(Jun)...
- Year 2028 (code 8): J8(Apr), K8(May), M8(Jun)...

### Product Mapping

All product names mapped to futures product categories:
```
HTT → HTT
HOUBR_Cross → HOUBR
HOUBR → HOUBR
CLBR → CLBR
HTT_Rolls → HTT
HOUBR_Boxes → HOUBR
CLBR_Boxes → CLBR
HTTMID → LH (Longhorn)
WDF → WDF
```

## Key Features

✓ **Comprehensive Tenor Support** - Handles all contract types (outright, quarterly, half, calendar, spreads)

✓ **Smart Spread Logic** - Properly divides multi-tenor legs and maintains net = 0

✓ **Product Mapping** - Automatically maps contract names to futures products

✓ **Chronological Sorting** - Tenor results sorted by date/quarter

✓ **Verification Built-in** - Includes test suite to validate expansions

✓ **Multiple Output Formats** - Both detailed (CSV) and summary (pivot table) views

## Example Input

From `pos_summary.csv`:
```
Qty,Tenor,Product,Strategy
100,H6,HTT,HTT_Front
-574,K6,HTT,HTT_Mid
-75,Cal27,HTT,HTT_Back
100,H2-26,HTT,HTT_Back
-1400,Q2-26/Q3-26,HTT Rolls,HTT_Rolls
-120,J6/Q2-26,WDF,Freight
```

## Example Output

From `delta_summary.csv`:
```
Tenor    HTT      HOUBR    CLBR     WDF      LH
H6       100.00   300.00   0.00     0.0      753.00
J6       0.00     -300.00  31.99    -105.0   0.00
K6       -574.00  0.00     0.00     0.0      0.00
N6       0.00     0.00     0.00     40.0     333.33
Q6       0.00     0.00     0.00     40.0     333.33
U6       0.00     0.00     0.00     40.0     333.33
```

## Validation Results

All 7 test cases pass:
- ✓ Simple outright contracts preserved
- ✓ Quarterly contracts split into 3 tenors
- ✓ Half-year contracts split into 6 tenors
- ✓ Calendar contracts split into 12 tenors
- ✓ Simple spreads balance to zero
- ✓ Complex spreads (Q vs Q) balance to zero
- ✓ Mixed spreads (outright vs quarterly) balance correctly

## Usage in Jupyter Notebook

To integrate with the existing `q_risk_report.ipynb`:

```python
from position_expander import expand_positions, create_delta_summary

# Expand all positions
delta_positions = expand_positions('pos_summary.csv')

# Create summary table
delta_summary = create_delta_summary(delta_positions)

# Display
print(delta_summary)
```

## Technical Details

### Algorithm
1. Parse input positions from CSV
2. For each position:
   - Detect tenor type (outright/quarterly/half/calendar/spread)
   - Expand to individual futures contracts
   - For spreads: expand both legs, apply signs, divide quantities
   - Map products using lookup table
3. Aggregate by (Tenor, Mapped_Product) pairs
4. Pivot into final summary table

### Computational Complexity
- Linear in number of input positions
- Each position expands to 1-12 rows (typically 1-3)
- ~100 total rows generated from 21 input positions

### Dependencies
- pandas (for data manipulation)
- Python 3.6+

## Files for Reference

- `IMPLEMENTATION_SUMMARY.md` - Detailed technical documentation
- `test_expansion.py` - Full test suite with examples
- `position_expander.py` - Complete source code with comments

---

**Status**: ✓ Complete and Tested
**Last Updated**: January 24, 2026
