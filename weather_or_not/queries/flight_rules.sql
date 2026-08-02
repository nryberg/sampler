-- flight_rules.sql
-- Classify each KMSP METAR observation into an FAA flight-rules category.
--
-- The category is the MORE RESTRICTIVE of the ceiling and the visibility:
--
--   Category  Ceiling (ft AGL)      Visibility (statute miles)
--   --------  --------------------  --------------------------
--   LIFR      below 500             below 1
--   IFR       500 to below 1,000    1 to below 3
--   MVFR      1,000 to 3,000        3 to 5
--   VFR       above 3,000           above 5
--
-- CEILING = the lowest BROKEN (BKN), OVERCAST (OVC) or obscured/vertical-
-- visibility (VV) layer. FEW and SCT layers are NOT ceilings, so a sky of
-- only FEW/SCT/CLR has an "unlimited" ceiling (represented here as 99999 ft).
--
-- METAR reports cloud layers in ascending altitude, so the FIRST BKN / OVC /
-- VV group in the raw text is the lowest one. Heights are in hundreds of feet
-- (e.g. OVC002 = 200 ft, BKN140 = 14,000 ft), so we multiply the 3 digits x100.
--
-- Run:  sqlite3 sqlite_Weather_Log.db ".read queries/flight_rules.sql"

WITH observed AS (
    -- drop the 2 blank rows and de-dupe repeat scrapes of the same timestamp
    SELECT Station, Observed_Date, Temp_Celsius, Wind_Speed, Wind_Direction,
           Cover, Visibility AS vis, Observation AS obs
    FROM Weather_History
    WHERE Station = 'KMSP'
    GROUP BY Station, Observed_Date
),
layers AS (
    SELECT *,
        instr(obs, 'BKN') AS pB,     -- position of first Broken layer
        instr(obs, 'OVC') AS pO,     -- position of first Overcast layer
        instr(obs, ' VV') AS pV      -- position of Vertical Visibility group
    FROM observed
),
ceiling AS (
    SELECT *,
        MIN(
            CASE WHEN pB > 0 THEN CAST(substr(obs, pB + 3, 3) AS INTEGER) * 100 ELSE 99999 END,
            CASE WHEN pO > 0 THEN CAST(substr(obs, pO + 3, 3) AS INTEGER) * 100 ELSE 99999 END,
            CASE WHEN pV > 0 THEN CAST(substr(obs, pV + 3, 3) AS INTEGER) * 100 ELSE 99999 END
        ) AS ceiling_ft
    FROM layers
),
classified AS (
    SELECT
        Observed_Date,
        Temp_Celsius,
        Wind_Speed,
        Cover,
        vis                                                       AS visibility_sm,
        CASE WHEN ceiling_ft = 99999 THEN NULL ELSE ceiling_ft END AS ceiling_ft,
        CASE
            WHEN ceiling_ft < 500  OR vis < 1 THEN 'LIFR'
            WHEN ceiling_ft < 1000 OR vis < 3 THEN 'IFR'
            WHEN ceiling_ft <= 3000 OR vis <= 5 THEN 'MVFR'
            ELSE 'VFR'
        END AS flight_rules
    FROM ceiling
)
SELECT * FROM classified
ORDER BY Observed_Date;
