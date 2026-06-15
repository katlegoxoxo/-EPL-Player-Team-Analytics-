
import pandas as pd
import re
import numpy as np

# ─────────────────────────────────────────────
# SECTION 1 — LOAD RAW FILES
# ─────────────────────────────────────────────

df_fbref    = pd.read_csv("2024fbref.csv",                    encoding="latin1", sep="\t",   skiprows=2, on_bad_lines="skip")
df_tm       = pd.read_csv("epl_transfermarkt_2024_25.csv",    encoding="latin1",              on_bad_lines="skip")


print(f"Loaded — FBref: {df_fbref.shape} | Transfermarkt: {df_tm.shape} ")


# ─────────────────────────────────────────────
# SECTION 2 — CLEAN FBREF
# ─────────────────────────────────────────────

# Assign clean column names (file has duplicate names like Gls, Gls per 90)
df_fbref.columns = [
    "Rk", "Player", "Nation", "Pos", "Squad", "Age", "Born",
    "MP", "Starts", "Min", "90s",
    "Gls", "Ast", "G+A", "G-PK", "PK", "PKatt", "CrdY", "CrdR",
    "Gls_p90", "Ast_p90", "GA_p90", "GxPK_p90", "GApK_p90",
    "Matches"
]

# Keep only real data rows (Rk must be a number)
df_fbref = df_fbref[df_fbref["Rk"].apply(lambda x: str(x).strip().isdigit())].copy()

# Clean minutes — remove commas, convert to int
df_fbref["Min"] = df_fbref["Min"].astype(str).str.replace(",", "").str.strip()
df_fbref["Min"] = pd.to_numeric(df_fbref["Min"], errors="coerce")

# Extract 3-letter nation code from "eng ENG" → "ENG"
df_fbref["Nation_Code"] = df_fbref["Nation"].str.strip().str.split().str[-1]

# Convert numeric columns
num_cols = ["Rk","Age","Born","MP","Starts","90s","Gls","Ast","G+A","G-PK",
            "PK","PKatt","CrdY","CrdR","Gls_p90","Ast_p90","GA_p90","GxPK_p90","GApK_p90"]
for col in num_cols:
    df_fbref[col] = pd.to_numeric(df_fbref[col], errors="coerce")

# Normalize squad names to a standard set
fbref_team_map = {
    "Manchester Utd":    "Manchester United",
    "Wolves":            "Wolverhampton Wanderers",
    "Brighton":          "Brighton & Hove Albion",
    "Bournemouth":       "AFC Bournemouth",
    "Ipswich Town":      "Ipswich Town",
    "Nottingham Forest": "Nottingham Forest",
}
df_fbref["Team"] = df_fbref["Squad"].replace(fbref_team_map)

# Drop players with fewer than 90 minutes (less than 1 full game)
before = len(df_fbref)
df_fbref = df_fbref[df_fbref["Min"] >= 90].copy()
print(f"FBref — dropped {before - len(df_fbref)} players under 90 mins → {len(df_fbref)} remain")

# Drop unused columns
df_fbref = df_fbref.drop(columns=["Rk", "Nation", "Squad", "Matches"], errors="ignore")

# Rename for clarity
df_fbref = df_fbref.rename(columns={
    "Player":    "player_fbref",
    "Pos":       "position_abbr",
    "Age":       "age",
    "Born":      "birth_year",
    "MP":        "matches_played",
    "Starts":    "starts",
    "Min":       "minutes",
    "90s":       "nineties",
    "Gls":       "goals",
    "Ast":       "assists",
    "G+A":       "goal_contributions",
    "G-PK":      "goals_excl_pk",
    "PK":        "pk_scored",
    "PKatt":     "pk_attempted",
    "CrdY":      "yellow_cards",
    "CrdR":      "red_cards",
    "Gls_p90":   "goals_p90",
    "Ast_p90":   "assists_p90",
    "GA_p90":    "ga_p90",
    "GxPK_p90":  "goals_excl_pk_p90",
    "GApK_p90":  "ga_excl_pk_p90",
})

print(f"FBref clean — {len(df_fbref)} rows, {df_fbref.shape[1]} columns")
print(df_fbref.head(3))


# ─────────────────────────────────────────────
# SECTION 3 — CLEAN TRANSFERMARKT
# ─────────────────────────────────────────────

# Clean player name — remove jersey number prefix and whitespace/newlines
# Raw format: "#41\n\n   Declan Rice"
df_tm["player_tm"] = (
    df_tm["Player"]
    .str.replace(r"#\d+", "", regex=True)   # remove #41 prefix
    .str.replace(r"\s+", " ", regex=True)   # collapse all whitespace/newlines
    .str.strip()
)

# Extract age from "14/01/1999 (27)" → 27
df_tm["age_numeric"] = (
    df_tm["Age"]
    .str.extract(r"\((\d+)\)")
    .astype(float)
)

# Extract date of birth from "14/01/1999 (27)" → "1999-01-14"
df_tm["dob"] = pd.to_datetime(
    df_tm["Age"].str.extract(r"(\d{2}/\d{2}/\d{4})")[0],
    format="%d/%m/%Y",
    errors="coerce"
).dt.strftime("%Y-%m-%d")

# Clean nationality — remove encoding garbage (Â, \xa0 etc), take first nationality only
df_tm["nationality"] = (
    df_tm["Nationality"]
    .str.encode("latin1", errors="replace")
    .str.decode("ascii", errors="replace")
    .str.replace(r"[^a-zA-Z\s]", " ", regex=True)   # remove garbage chars
    .str.strip()
    .str.split()
    .str[0]   # take first word (primary nationality)
)

# Normalize preferred foot
df_tm["preferred_foot"] = df_tm["Preferred_Foot"].str.strip().str.lower()

# Extract clean position (drop "Midfield - " prefix → "Central Midfield")
df_tm["position_detailed"] = (
    df_tm["Position"]
    .str.replace(r"^(Midfield|Defender|Forward|Goalkeeper|Attack)\s*-\s*", "", regex=True)
    .str.strip()
)

# Normalize team names to standard
tm_team_map = {
    "Arsenal":                   "Arsenal",
    "AFC Bournemouth":           "AFC Bournemouth",
    "Aston Villa":               "Aston Villa",
    "Brentford":                 "Brentford",
    "Brighton & Hove Albion":    "Brighton & Hove Albion",
    "Chelsea":                   "Chelsea",
    "Crystal Palace":            "Crystal Palace",
    "Everton":                   "Everton",
    "Fulham":                    "Fulham",
    "Ipswich Town":              "Ipswich Town",
    "Leicester City":            "Leicester City",
    "Liverpool":                 "Liverpool",
    "Manchester City":           "Manchester City",
    "Manchester United":         "Manchester United",
    "Newcastle United":          "Newcastle United",
    "Nottingham Forest":         "Nottingham Forest",
    "Southampton":               "Southampton",
    "Tottenham Hotspur":         "Tottenham Hotspur",
    "West Ham United":           "West Ham United",
    "Wolverhampton Wanderers":   "Wolverhampton Wanderers",
}
df_tm["Team"] = df_tm["Team"].replace(tm_team_map)

# Keep only what we need from Transfermarkt
df_tm = df_tm[["player_tm", "Team", "preferred_foot", "position_detailed", "age_numeric", "dob", "nationality"]].copy()

# Remove duplicate player-team combos (keep first)
before = len(df_tm)
df_tm = df_tm.drop_duplicates(subset=["player_tm", "Team"])
print(f"Transfermarkt — removed {before - len(df_tm)} duplicate rows → {len(df_tm)} remain")
print(df_tm.head(3))



# ─────────────────────────────────────────────
# SECTION 4 — MERGE ALL DATASETS
# ─────────────────────────────────────────────

# Step 1 — Normalize player names for fuzzy-safe joining (lowercase + strip)
df_fbref["player_key"] = df_fbref["player_fbref"].str.lower().str.strip()
df_tm["player_key"]    = df_tm["player_tm"].str.lower().str.strip()

# Step 2 — Merge FBref + Transfermarkt on player_key + Team
df_merged = pd.merge(
    df_fbref,
    df_tm,
    on=["player_key", "Team"],
    how="left"   # keep all FBref players; TM metadata fills in where available
)

print(f"\nFBref + TM merge:")
print(f"  Rows:          {len(df_merged)}")
print(f"  Matched (foot not null): {df_merged['preferred_foot'].notna().sum()}")
print(f"  Unmatched:     {df_merged['preferred_foot'].isna().sum()}")

# Step 3 — Add season tag
df_merged["season"] = "2024/25"

# Step 4 — Clean up key columns
df_merged = df_merged.rename(columns={
    "player_fbref": "player",
    "Nation_Code":  "nation_code",
})
df_merged = df_merged.drop(columns=["player_key", "player_tm"], errors="ignore")

# Reorder columns logically
col_order = [
    "season", "player", "Team", "nation_code", "nationality",
    "position_abbr", "position_detailed", "preferred_foot",
    "age", "birth_year", "dob",
    "matches_played", "starts", "minutes", "nineties",
    "goals", "assists", "goal_contributions", "goals_excl_pk",
    "pk_scored", "pk_attempted", "yellow_cards", "red_cards",
    "goals_p90", "assists_p90", "ga_p90", "goals_excl_pk_p90", "ga_excl_pk_p90",
]
# Only include columns that actually exist
col_order = [c for c in col_order if c in df_merged.columns]
df_merged = df_merged[col_order]

print(f"\nFinal merged dataset — {len(df_merged)} rows, {df_merged.shape[1]} columns")
print(df_merged.head(5).to_string())

# ─────────────────────────────────────────────
# SECTION 6 — QA CHECKS
# ─────────────────────────────────────────────

print("\n=== QA SUMMARY ===")
print(f"Total players:          {len(df_merged)}")
print(f"Teams represented:      {df_merged['Team'].nunique()}")
print(f"Avg minutes played:     {df_merged['minutes'].mean():.0f}")
print(f"Players with foot data: {df_merged['preferred_foot'].notna().sum()}")
print(f"Null goals:             {df_merged['goals'].isna().sum()}")
print(f"Null assists:           {df_merged['assists'].isna().sum()}")
print()
print("Position distribution:")
print(df_merged["position_abbr"].value_counts())
print()
print("Preferred foot:")
print(df_merged["preferred_foot"].value_counts(dropna=False))


# ─────────────────────────────────────────────
# SECTION 8 — EXPORT
# ─────────────────────────────────────────────

df_merged.to_csv("epl_combined_2024_25.csv", index=False)

print("   epl_combined_2024_25.csv       ← upload to Databricks as player stats table")
