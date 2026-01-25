"""
Reorganize position_mc_report_clean.ipynb per plan:
- Remove duplicates (8a/8b headers, analysis cells, 4d header)
- Reorder cells to match dependency flow
- Consolidate Analysis + bucket comparison into single 8f cell
- Rename Final Summary to Section 9
"""
import json
import sys

NOTEBOOK = "position_mc_report_clean.ipynb"
OUTPUT = "position_mc_report_clean.ipynb"

def src(cell):
    """Get source as single string."""
    s = cell.get("source", [])
    return "".join(s) if isinstance(s, list) else s

def first_line(cell):
    s = src(cell)
    return s.strip().split("\n")[0][:80] if s else ""

def is_markdown(cell):
    return cell.get("cell_type") == "markdown"

def fingerprint(cell):
    """Rough fingerprint for dedup/matching."""
    s = src(cell)
    f = first_line(cell)
    if "### 8a. Build Multi-Product Returns" in s and is_markdown(cell):
        return "8a_header"
    if "### 8b. Compute Multi-Product EWMA" in s and is_markdown(cell):
        return "8b_header"
    if "## 4d. Comprehensive Comparison" in s:
        return "4d_header"
    if "## 8. Multi-Product Covariance Matrix Analysis" in s or ("## 8. Multi-Product" in s and "cross-product" in s.lower()):
        return "8_intro"
    if "## 8. Final Summary" in s:
        return "8_final_header"
    if "## 5. Results DataFrame" in s:
        return "5_results_header"
    if "## 6. Aggregation" in s:
        return "6_header"
    if "## 7. Cross-Product" in s:
        return "7_header"
    if "## 5a. MC Results" in s:
        return "5a_header"
    if "Create position MC DataFrame" in s and "position_mc_df = pd.DataFrame(position_mc_results)" in s:
        return "position_mc_df_cell"
    if "Check if diagnostic_data" in s and "diagnostic_df" in s:
        return "diagnostics_cell"
    if "Build multi-product returns matrix" in s and "products_with_data" in s and "combined_returns_df" in s:
        return "8a_returns"
    if "compute_multi_product_ewma_covariance" in s and "Sigma_multi" in s:
        return "8b_sigma"
    if "Build combined position vectors" in s and "w_total_combined" in s:
        return "8c_combined"
    if "POSITION VECTOR ANALYSIS" in s and "pos_analysis_df" in s:
        return "position_analysis"
    if "Recalculate MC for each strategy/product using multi-product" in s and "position_mc_multi_product" in s:
        return "8d_recalc"
    if "Calculate MC by bucket using shared covariance" in s and "mc_by_bucket_shared" in s:
        return "8e_mc_bucket"
    if "Bucket-level comparison between independent and shared" in s:
        return "bucket_comparison"
    if "Analysis and comparison" in s and "position_mc_multi_product" in s and "MULTI-PRODUCT COVARIANCE ANALYSIS" in s:
        return "analysis_cell"
    if "Aggregate by Strategy (across all products)" in s and "mc_by_strategy" in s:
        return "6_aggregation"
    if "Cross-product summary" in s and "strategy_product_pivot" in s:
        return "7_cross_product"
    if "Create MC lookup DataFrame from position_mc_results" in s and "pos_summary_with_mc" in s:
        return "5a_pos_summary"
    if "POSITION MC REPORT - FINAL SUMMARY" in s and "mc_by_strategy" in s:
        return "final_summary"
    return None

def main():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb["cells"]
    by_fp = {}
    for i, c in enumerate(cells):
        fp = fingerprint(c)
        if fp:
            by_fp.setdefault(fp, []).append((i, c))
        else:
            by_fp.setdefault(f"cell_{i}", []).append((i, c))

    # Collect non-duplicate cells we care about (first occurrence)
    used = {}
    for fp, lst in by_fp.items():
        used[fp] = lst[0][1]

    # Build 8f consolidated cell: analysis + bucket comparison
    analysis = used.get("analysis_cell")
    bucket = used.get("bucket_comparison")
    if not analysis or not bucket:
        print("Missing analysis or bucket cell", file=sys.stderr)
        sys.exit(1)

    analysis_src = src(analysis)
    # Add bucket-level comparison section before INTERPRETATION (keep else clause)
    if 'print("INTERPRETATION")' in analysis_src and "Bucket-level comparison" not in analysis_src:
        insert = '''

    # Bucket-level comparison (independent vs shared, direct vs aggregated)
    print(f"\\n" + "="*80)
    print("MC BY BUCKET COMPARISON")
    print("="*80)
    
    bucket_map = {}
    for result in position_mc_results:
        key = (result['Strategy'], result['Product'])
        bucket_map[key] = result.get('Bucket', 'Unknown')
    
    comparison_df['Bucket'] = comparison_df.apply(
        lambda row: bucket_map.get((row['Strategy'], row['Product']), 'Unknown'), 
        axis=1
    )
    
    mc_by_bucket_original = comparison_df.groupby('Bucket').agg({'MC_original': 'sum'}).reset_index()
    mc_by_bucket_original.columns = ['Bucket', 'MC_independent']
    mc_by_bucket_multi = comparison_df.groupby('Bucket').agg({'MC_multi_product': 'sum'}).reset_index()
    mc_by_bucket_multi.columns = ['Bucket', 'MC_shared']
    mc_bucket_comparison = mc_by_bucket_original.merge(mc_by_bucket_multi, on='Bucket', how='outer').fillna(0.0)
    mc_bucket_comparison['Difference'] = mc_bucket_comparison['MC_shared'] - mc_bucket_comparison['MC_independent']
    mc_bucket_comparison['Pct_change'] = (mc_bucket_comparison['Difference'] / mc_bucket_comparison['MC_independent'].abs() * 100).replace([np.inf, -np.inf], 0.0)
    mc_bucket_comparison = mc_bucket_comparison.sort_values('Bucket')
    
    print("\\nMC by Bucket - Independent vs Shared Covariance:")
    print(mc_bucket_comparison.to_string(index=False))
    
    print("\\nBucket-level impact of cross-product correlations:")
    for _, row in mc_bucket_comparison.iterrows():
        if abs(row['Difference']) > 1:
            print(f"  {row['Bucket']}: {row['MC_independent']:.2f} -> {row['MC_shared']:.2f} ({row['Difference']:+.2f}, {row['Pct_change']:+.2f}%)")
    
    if 'mc_by_bucket_shared' in globals() and len(mc_by_bucket_shared) > 0:
        print("\\n" + "="*80)
        print("DIRECT BUCKET MC vs AGGREGATED (from strategies)")
        print("="*80)
        bucket_direct_vs_agg = mc_by_bucket_shared[['Bucket', 'MC_to_total']].copy()
        bucket_direct_vs_agg.columns = ['Bucket', 'MC_direct']
        bucket_direct_vs_agg = bucket_direct_vs_agg.merge(mc_bucket_comparison[['Bucket', 'MC_shared']], on='Bucket', how='outer').fillna(0.0)
        bucket_direct_vs_agg['Difference'] = bucket_direct_vs_agg['MC_direct'] - bucket_direct_vs_agg['MC_shared']
        print(bucket_direct_vs_agg.to_string(index=False))
        print("\\nNote: Direct = bucket position vectors; Aggregated = sum of strategy/product MCs by bucket.")

'''
        # Insert before INTERPRETATION block
        marker = '    print(f"\\n" + "="*80)\n    print("INTERPRETATION")'
        idx = analysis_src.find(marker)
        if idx >= 0:
            analysis_src = analysis_src[:idx] + insert + analysis_src[idx:]
        else:
            analysis_src = analysis_src + insert

    if "Bucket-level analysis" not in analysis_src and "INTERPRETATION" in analysis_src:
        analysis_src = analysis_src.replace(
            "- The difference between independence and multi-product MC shows the impact of these correlations\n",
            "- The difference between independence and multi-product MC shows the impact of these correlations\n- Bucket-level analysis shows how cross-product correlations affect risk in different tenor buckets\n"
        )

    lines = analysis_src.split("\n")
    eight_f = {"cell_type": "code", "metadata": {}, "source": [x + "\n" for x in lines]}
    eight_f.setdefault("outputs", [])
    eight_f["execution_count"] = None

    # Build ordered list of cells by logical section
    def code_cell(c):
        out = {k: v for k, v in c.items() if k in ("cell_type", "metadata", "source")}
        if "outputs" in c:
            out["outputs"] = []
        if "execution_count" in c:
            out["execution_count"] = None
        return out

    def md_cell(lines):
        return {"cell_type": "markdown", "metadata": {}, "source": [lines] if isinstance(lines, str) else lines}

    ordered = []

    # 1. Title
    for i, c in enumerate(cells):
        if "Position MC Report" in first_line(c) and is_markdown(c):
            ordered.append(c)
            break

    # 2. Imports
    for i, c in enumerate(cells):
        if "import pandas" in first_line(c) and "import numpy" in src(c):
            ordered.append(code_cell(c))
            break

    # 3. ## 1 Config
    ordered.append(md_cell("## 1. Configuration & Data Loading\n"))
    for i, c in enumerate(cells):
        if "CONFIGURATION - Reuse" in src(c) and "front = " in src(c):
            ordered.append(code_cell(c))
            break

    # 4. ## 2 Functions
    ordered.append(md_cell("## 2. Reuse Functions from q_risk_report.ipynb\n"))
    for i, c in enumerate(cells):
        if "def compute_ewma_covariance" in src(c) and "def compute_mc_to_total" in src(c):
            ordered.append(code_cell(c))
            break

    # 5. ## 3 Strategy mapping
    ordered.append(md_cell("## 3. Strategy Position Mapping\n"))
    for i, c in enumerate(cells):
        if "def build_strategy_position_vector" in src(c) and "def determine_bucket" in src(c):
            ordered.append(code_cell(c))
            break

    # 6. ## 4 Single Product MC
    ordered.append(md_cell("## 4. Single Product MC Calculation\n"))
    for i, c in enumerate(cells):
        if "Get all unique mapped products from delta_positions" in src(c) and "position_mc_results = []" in src(c):
            ordered.append(code_cell(c))
            break

    # 7. ## 5 Results: diagnostics + position_mc_df
    ordered.append(md_cell("## 5. Results DataFrame\n"))
    if "diagnostics_cell" in used:
        ordered.append(code_cell(used["diagnostics_cell"]))
    ordered.append(code_cell(used["position_mc_df_cell"]))

    # 8. ## 6 Aggregation
    ordered.append(md_cell("## 6. Aggregation by Strategy and Product\n"))
    ordered.append(code_cell(used["6_aggregation"]))

    # 9. ## 7 Cross-Product
    ordered.append(md_cell("## 7. Cross-Product MC Summary\n"))
    ordered.append(code_cell(used["7_cross_product"]))

    # 10. ## 5a pos_summary
    ordered.append(md_cell("## 5a. MC Results in pos_summary Format\n"))
    ordered.append(code_cell(used["5a_pos_summary"]))

    # 11. ## 8 Multi-Product intro
    ordered.append(md_cell("## 8. Multi-Product Covariance Matrix Analysis\n\nThis section uses a shared covariance matrix across all products (cross-product correlations), compared to the independence assumption in sections 6–7.\n"))

    # 12. 8a returns
    ordered.append(md_cell("### 8a. Build Multi-Product Returns Matrix\n"))
    ordered.append(code_cell(used["8a_returns"]))

    # 13. 8b Sigma_multi
    ordered.append(md_cell("### 8b. Compute Multi-Product EWMA Covariance Matrix\n"))
    ordered.append(code_cell(used["8b_sigma"]))

    # 14. 8c combined
    ordered.append(md_cell("### 8c. Build Combined Position Vectors\n"))
    ordered.append(code_cell(used["8c_combined"]))

    # 15. Optional position analysis
    if "position_analysis" in used:
        ordered.append(code_cell(used["position_analysis"]))

    # 16. 8d Recalculate MC
    ordered.append(md_cell("### 8d. Recalculate MC with Multi-Product Covariance\n"))
    ordered.append(code_cell(used["8d_recalc"]))

    # 17. 8e MC by bucket
    ordered.append(md_cell("### 8e. MC by Bucket (Shared Covariance)\n"))
    ordered.append(code_cell(used["8e_mc_bucket"]))

    # 18. 8f Analysis + bucket comparison (consolidated)
    ordered.append(md_cell("### 8f. Analysis and Comparison\n"))
    ordered.append(eight_f)

    # 19. ## 9 Final Summary
    ordered.append(md_cell("## 9. Final Summary\n"))
    ordered.append(code_cell(used["final_summary"]))

    # Normalize sources to list of lines ending in \n
    for c in ordered:
        if c["cell_type"] == "code" and "source" in c:
            s = c["source"]
            if isinstance(s, list):
                lines = []
                for line in s:
                    l = line if isinstance(line, str) else str(line)
                    if not l.endswith("\n"):
                        l += "\n"
                    lines.append(l)
                c["source"] = lines
            else:
                c["source"] = [t + "\n" for t in s.split("\n")[:-1]] + ([s.split("\n")[-1] + "\n"] if s.split("\n")[-1] else [])

    nb["cells"] = ordered
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print("Reorganized", len(ordered), "cells ->", OUTPUT)

if __name__ == "__main__":
    main()
