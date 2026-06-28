# Data Sources — Budget

## opp_1961_2010.csv
OPP "Ejecución Presupuestal 1961-2010"
- Note: download URL unknown. Guessing: catalogodatos.gub.uy or opp.gub.uy
- Format: wide CSV, semicolon-delimited, European numbers (period=thousands sep, comma=decimal)
- Unit: thousands of pesos uruguayos

## opp_2011_2025.csv
OPP "Crédito Presupuestal 2011-2025"
- Note: download URL unknown. Guess: catalogodatos.gub.uy or opp.gub.uy
- Format: long CSV, comma-delimited
- Unit: pesos uruguayos (not thousands)
- Columns: AÑO, Organismo_nombre, AP_nombre, Ejecutado, ...
- WARNING: downloaded mid-2025 — 2025 rows are partial

## wb_gdp_const_usd.csv
World Bank NY.GDP.MKTP.KD — GDP constant 2015 USD
- Source certain: data.worldbank.org, indicator NY.GDP.MKTP.KD (from plot caption)
- 1960–2024 from WB; 2025 derived as 2024 × 1.018 (BCU 1.8% real growth, base year mismatch WB=2015 vs BCU=2016)

## wb_gdp_nominal_pesos.csv
World Bank NY.GDP.MKTP.CN — GDP current pesos
- Source certain: data.worldbank.org, indicator NY.GDP.MKTP.CN (from plot caption)
- 1960–2024 from WB; 2025 = 3,516,000,000,000 pesos from BCU Q4-2025 report (certain)
- Note: WB has 3.256T for 2024, BCU revised to 3.310T — kept WB for historical consistency

## wb_exp_pct_gdp.csv + budget.csv
World Bank GC.XPN.TOTL.GD.ZS (expense) + GC.DOD.TOTL.GD.ZS (debt)
- Source: data.worldbank.org

## informe-de-cuentas-nacionales-trimestrales_2025_IV.pdf
Banco Central del Uruguay — Informe de Cuentas Nacionales Trimestrales Q4-2025
- URL: https://www.bcu.gub.uy/Estadisticas-e-Indicadores/Cuentas%20Nacionales/Informe%20de%20Cuentas%20Nacionales%20Trimestrales_2025_IV.pdf
- Key figures: 2025 real growth 1.8%, 2025 nominal GDP 3.516T UYU, 2024 nominal revised 3.310T UYU
