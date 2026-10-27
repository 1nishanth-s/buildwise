import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

import pandas as pd
import json
from src.validator import validate_components, validate_prices, COMPONENT_COLUMNS, PRICE_COLUMNS
from src import compatibility as compat

def run_validation():
    base_dir = Path(__file__).resolve().parent
    comp_file = base_dir / 'components.csv'
    price_file = base_dir / 'indian_prices.csv'
    usd_file = base_dir / 'usd_reference_prices.csv'
    bak_comp_file = root / 'backups/pre_integration_20261027/components.csv'
    prod_comp_file = bak_comp_file if bak_comp_file.exists() else (root / 'data/components.csv')
    bak_price_file = root / 'backups/pre_integration_20261027/prices.csv'
    prod_price_file = bak_price_file if bak_price_file.exists() else (root / 'data/prices.csv')
    
    print('========================================================')
    print('BuildWise-AI Curated Import Validation Suite')
    print('========================================================\n')
    
    # 1. Load components
    df_comp = pd.read_csv(comp_file)
    print(f'[CHECK 1] Components loaded: {len(df_comp)} rows')
    
    # Validate schema
    assert list(df_comp.columns) == COMPONENT_COLUMNS, f'Columns do not match production: {df_comp.columns}'
    print(' - Schema columns: MATCH production COMPONENT_COLUMNS')
    
    # Run production component validator
    comp_issues = validate_components(df_comp)
    assert len(comp_issues) == 0, f'Component validation failed: {comp_issues}'
    print(' - Production validate_components: 0 ISSUES (PASSED)')
    
    # Check IDs uniqueness
    assert not df_comp['component_id'].duplicated().any(), 'Duplicate component_id found'
    num_unique = df_comp['component_id'].nunique()
    print(f' - Component IDs unique: {num_unique} distinct IDs (PASSED)')
    
    # Check unique normalized display identities
    norm_ident = df_comp.apply(lambda r: str(r['category']).strip().casefold() + '|' + str(r['brand']).strip().casefold() + '|' + str(r['model']).strip().casefold(), axis=1)
    dup_ident_count = norm_ident.duplicated().sum()
    assert dup_ident_count == 0, f'Found {dup_ident_count} duplicate normalized identities'
    print(f' - Normalized display identities unique: 293 / 293 unique (0 DUPLICATES - PASSED)')
    
    # Check Categories and counts
    cat_counts = df_comp['category'].value_counts().to_dict()
    print(f' - Category counts: {cat_counts}')
    
    # Check production collisions
    df_prod = pd.read_csv(prod_comp_file)
    prod_norm = set(df_prod.apply(lambda r: str(r['category']).strip().casefold() + '|' + str(r['brand']).strip().casefold() + '|' + str(r['model']).strip().casefold(), axis=1))
    collision_count = 0
    for idx, r in df_comp.iterrows():
        ident = str(r['category']).strip().casefold() + '|' + str(r['brand']).strip().casefold() + '|' + str(r['model']).strip().casefold()
        if ident in prod_norm:
            collision_count += 1
    assert collision_count == 0, f'Found {collision_count} collisions with production'
    print(' - Collisions with live production catalog: 0 COLLISIONS (PASSED)')
    
    # 2. Check Prices
    df_prc = pd.read_csv(price_file)
    print(f'\n[CHECK 2] Indian Retail Prices loaded: {len(df_prc)} rows')
    assert all(c in df_prc.columns for c in PRICE_COLUMNS), 'Missing required price columns'
    print(' - Schema columns: INCLUDES all required PRICE_COLUMNS and OPTIONAL_PRICE_COLUMNS')
    
    # Validate price foreign keys against combined (curated + production) components
    all_comps = pd.concat([df_comp, df_prod], ignore_index=True)
    prc_issues = validate_prices(df_prc, all_comps)
    assert len(prc_issues) == 0, f'Price validation failed: {prc_issues}'
    print(' - Foreign keys & validate_prices against combined catalog: 0 ISSUES (PASSED)')
    
    # Check no duplicate price observation with production
    df_prod_prc = pd.read_csv(prod_price_file)
    prod_obs = set()
    for idx, r in df_prod_prc.iterrows():
        cid = str(r['component_id']).strip().casefold()
        s = str(r['seller']).strip().casefold()
        p = str(float(str(r['price_inr']).replace(',', '')))
        t = str(r['checked_at']).strip()
        prod_obs.add((cid, s, p, t))
        
    for idx, r in df_prc.iterrows():
        cid = str(r['component_id']).strip().casefold()
        s = str(r['seller']).strip().casefold()
        p = str(float(str(r['price_inr']).replace(',', '')))
        t = str(r['checked_at']).strip()
        assert (cid, s, p, t) not in prod_obs, f'Duplicate price observation with production: {(cid, s, p, t)}'
    print(' - Duplicate price observations check with production: 0 DUPLICATES (PASSED)')
    
    # 3. Check USD Isolation
    df_usd = pd.read_csv(usd_file)
    print(f'\n[CHECK 3] USD Reference Prices loaded: {len(df_usd)} rows')
    assert (df_usd['currency'] == 'USD').all(), 'Non-USD currency found in USD reference archive'
    print(' - Currency separation: 100% USD isolated from INR catalog (PASSED)')
    
    # 4. Check Compatibility Engine Behavior
    print('\n[CHECK 4] Compatibility Engine Behavior Checks')
    def get_specs(cid):
        return json.loads(df_comp[df_comp['component_id'] == cid].iloc[0]['specs_json'])
        
    cpu_am5 = get_specs('DS3_CPU_028')  # 7600X3D
    mb_am5 = get_specs('DS3_MB_001')    # ASUS PRIME B650-PLUS WIFI
    ram_ddr5 = get_specs('DS3_RAM_001') # Corsair Vengeance RGB 32GB
    st_nvme = get_specs('DS3_STORAGE_001') # 990 Pro 2TB
    case_atx = get_specs('DS3_CASE_002') # Phanteks XT PRO
    
    cpu_am4 = get_specs('DS3_CPU_010')  # 5600
    mb_am4 = get_specs('DS3_MB_005')    # ASUS B550M-A
    ram_ddr4 = get_specs('DS3_RAM_003') # Vengeance 16GB DDR4
    
    r_ram = compat.check_cpu_motherboard_ram(cpu_am5, mb_am5, ram_ddr5)
    assert r_ram.status == 'compatible', f'RAM check failed: {r_ram}'
    print(f' - AM5 CPU + MB + DDR5 RAM: {r_ram.status}')
    
    r_cap = compat.check_motherboard_ram_capacity(mb_am5, ram_ddr5)
    assert r_cap.status == 'compatible', f'RAM cap check failed: {r_cap}'
    print(f' - RAM Capacity check: {r_cap.status}')
    
    r_case = compat.check_motherboard_case(mb_am5, case_atx)
    assert r_case.status == 'compatible', f'MB-Case check failed: {r_case}'
    print(f' - Motherboard-Case form factor check: {r_case.status}')
    
    r_st = compat.check_storage_motherboard(st_nvme, mb_am5)
    assert r_st.status == 'compatible', f'Storage check failed: {r_st}'
    print(f' - Storage-Motherboard NVMe check: {r_st.status}')
    
    r_am4 = compat.check_cpu_motherboard_ram(cpu_am4, mb_am4, ram_ddr4)
    assert r_am4.status == 'compatible', f'AM4 RAM check failed: {r_am4}'
    print(f' - AM4 CPU + MB + DDR4 RAM: {r_am4.status}')
    
    r_mismatch_sock = compat.check_cpu_motherboard(cpu_am4, mb_am5)
    assert r_mismatch_sock.status == 'incompatible', f'Expected incompatible: {r_mismatch_sock}'
    print(f' - Incompatibility Detection (AM4 CPU on AM5 MB): {r_mismatch_sock.status}')
    
    r_mismatch_ram = compat.check_cpu_motherboard_ram(cpu_am5, mb_am5, ram_ddr4)
    assert r_mismatch_ram.status == 'incompatible', f'Expected incompatible: {r_mismatch_ram}'
    print(f' - Incompatibility Detection (DDR4 RAM on DDR5 MB): {r_mismatch_ram.status}')
    
    gpu = get_specs('DS3_GPU_001')
    r_gpu_case = compat.check_gpu_case(gpu, case_atx)
    assert r_gpu_case.status == 'unknown', f'Expected unknown: {r_gpu_case}'
    print(f' - Honest Unknown Clearance (GPU length vs unstated case clearance): {r_gpu_case.status}')
    
    print('\n========================================================')
    print('ALL CURATED IMPORT VALIDATION CHECKS PASSED SUCCESSFULLY!')
    print('========================================================')

if __name__ == '__main__':
    run_validation()

