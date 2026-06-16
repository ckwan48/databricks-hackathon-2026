## Column Semantics & Unit Audit (every column validated against the data)

*For each column the unit/type is inferred from the NAME and then VALIDATED against actual values. The unit is per-column: `*_pct`=percentage (0–100), `sex_ratio_*`=females per 1,000 males, `*_interviewed`/`*_surveyed`=respondent counts, OOP expenditure=Indian rupees, `hh`=household; facilities adds booleans, years, dates, coordinates and JSON arrays.*

### Validation headline
- **NFHS percentages:** all 101 `_pct` columns fall within **[0.0, 100.0]** ⇒ every percentage column's data matches its name. No `_pct` column exceeds 100.
- **Sex ratios** (per 1,000): total 755–1332; at-birth 658–1485 ⇒ correctly a per-1,000 ratio, NOT a percentage.
- **OOP delivery expenditure:** ₹0–₹20101 ⇒ rupees, must never be averaged with the % columns.
- **Sample-size counts:** households median 908, women median 1,020, men median 145 ⇒ counts, not indicators; the small men-count gates male-indicator reliability.
- **Name→unit contradictions found:** [('sex_ratio_at_birth_5y_f_per_1000_m', 'ratio: F per 1000 M', np.float64(658.0), np.float64(1485.0), '⚠ sex-ratio extreme')]

### Pincode (11): types
`pincode` = 6-digit identifier (not a quantity); `latitude`/`longitude` = geo floats (India bbox); `circlename/regionname/divisionname/district/statename` = categorical text (hierarchy); `officetype` = categorical (HO/SO/BO); `delivery` = binary.

### Facilities (51): data-driven types
Numeric quantities: `numberDoctors`, `capacity`, `engagement_metrics_*`, `post_metrics_post_count`, `number_of_facts_about_the_organization`, `distinct_social_media_presence_count`. Year: `yearEstablished`. Booleans: `acceptsVolunteers`, `affiliated_staff_presence`, `custom_logo_presence`. Dates: `post_metrics_most_recent_social_media_post_date`, `recency_of_page_update`. Geo: `latitude`/`longitude`/`coordinates`. JSON arrays: source_types, source_ids, phone_numbers, websites, specialties, procedure, equipment, capability, source_urls, countries, affiliationTypeIds. Categorical: `facilityTypeId`, `operatorTypeId`, `address_countryCode`. Identifiers/text: `unique_id`, `cluster_id`, `name`, emails, URLs, address lines.
**Data-quality flags:** `farmacy` & `pharmacy` both appear (same concept, normalize); one row has a coordinates-JSON string in `facilityTypeId` (a column-shifted row); `yearEstablished` future/implausible count checked above.

### nfhs5.csv — unit validated against data (109 cols)
| Column | Unit (validated) | observed min | observed max | missing |
|---|---|---|---|---|
| `district_name` | identifier | — | — | text |
| `state_ut` | identifier | — | — | text |
| `households_surveyed` | count: respondents | 213 | 990 | 0% sup |
| `women_15_49_interviewed` | count: respondents | 216 | 1621 | 0% sup |
| `men_15_54_interviewed` | count: respondents | 17 | 241 | 0% sup |
| `female_population_age_6_years_and_above_ever_schooled_pct` | percentage 0–100 | 45.4 | 99.2 | 0% sup |
| `population_below_age_15_years_pct` | percentage 0–100 | 16 | 50.6 | 0% sup |
| `sex_ratio_total_f_per_1000_m` | ratio: F per 1000 M | 755 | 1332 | 0% sup |
| `sex_ratio_at_birth_5y_f_per_1000_m` | ratio: F per 1000 M | 658 | 1485 | 0% sup |
| `child_u5_whose_birth_was_civil_reg_pct` | percentage 0–100 | 51.6 | 100 | 0% sup |
| `deaths_in_the_last_3_years_civil_reg_pct` | percentage 0–100 | 8.3 | 100 | 0% sup |
| `hh_electricity_pct` | percentage 0–100 | 68.4 | 100 | 0% sup |
| `hh_improved_water_pct` | percentage 0–100 | 41.2 | 100 | 0% sup |
| `hh_use_improved_sanitation_pct` | percentage 0–100 | 29.2 | 99.9 | 0% sup |
| `households_using_clean_fuel_for_cooking_pct` | percentage 0–100 | 8.6 | 99.8 | 0% sup |
| `households_using_iodized_salt_pct` | percentage 0–100 | 47.9 | 100 | 0% sup |
| `hh_member_covered_health_insurance_pct` | percentage 0–100 | 1.2 | 97.8 | 0% sup |
| `child_5y_who_attended_pre_primary_school_during_the_school_pct` | percentage 0–100 | 0 | 52.9 | 0% sup |
| `women_age_15_49_who_are_literate_pct` | percentage 0–100 | 38.6 | 99.7 | 0% sup |
| `women_age_15_49_with_10_or_more_years_of_schooling_pct` | percentage 0–100 | 13.6 | 88.2 | 0% sup |
| `w20_24_married_before_age_18_years_pct` | percentage 0–100 | 0 | 57.6 | 0% sup |
| `births_in_the_5_years_preceding_the_survey_that_are_birth_3_pct` | percentage 0–100 | 0 | 8 | 0% sup |
| `w15_19_who_were_already_mothers_or_pregnant_at_the_time_of_pct` | percentage 0–100 | 0 | 27.3 | 0% sup |
| `w15_24_who_use_menstrual_hygiene_pct` | percentage 0–100 | 9 | 100 | 0% sup |
| `fp_cm_w15_49_any_method_pct` | percentage 0–100 | 12.1 | 89.1 | 0% sup |
| `fp_cm_w15_49_modern_method_pct` | percentage 0–100 | 10.6 | 81.2 | 0% sup |
| `fp_cm_w15_49_f_steril_pct` | percentage 0–100 | 1.1 | 76.5 | 0% sup |
| `fp_cm_w15_49_m_steril_pct` | percentage 0–100 | 0 | 18.4 | 0% sup |
| `fp_cm_w15_49_iud_pct` | percentage 0–100 | 0 | 32.2 | 0% sup |
| `fp_cm_w15_49_pill_pct` | percentage 0–100 | 0 | 53 | 0% sup |
| `fp_cm_w15_49_condom_pct` | percentage 0–100 | 0 | 43.9 | 0% sup |
| `fp_cm_w15_49_injectables_pct` | percentage 0–100 | 0 | 9.8 | 0% sup |
| `fp_unmet_total_cm_w15_49_7_pct` | percentage 0–100 | 1.2 | 33 | 0% sup |
| `fp_unmet_spacing_cm_w15_49_7_pct` | percentage 0–100 | 0.3 | 25.2 | 0% sup |
| `health_worker_ever_talked_to_female_non_users_about_family_pct` | percentage 0–100 | 2 | 64.2 | 0% sup |
| `current_users_ever_told_about_side_effects_of_current_metho_pct` | percentage 0–100 | 14.6 | 98.9 | 0% sup |
| `mothers_who_had_an_anc_visit_in_the_first_trimester_lb5y_pct` | percentage 0–100 | 26.3 | 99.6 | 0% sup |
| `mothers_who_had_at_least_4_anc_visits_lb5y_pct` | percentage 0–100 | 4.4 | 98.7 | 0% sup |
| `mothers_whose_last_birth_was_protected_against_neo_tetanus_pct` | percentage 0–100 | 55.1 | 100 | 0% sup |
| `mothers_who_consumed_ifa_for_100_days_or_more_when_they_wer_pct` | percentage 0–100 | 1.6 | 95 | 0% sup |
| `mothers_who_consumed_ifa_for_180_days_or_more_when_they_wer_pct` | percentage 0–100 | 0.8 | 84.6 | 0% sup |
| `registered_pregnancies_for_which_the_mother_received_a_mcp_pct` | percentage 0–100 | 50 | 100 | 0% sup |
| `mothers_who_received_pnc_from_a_doctor_nurse_lhv_anm_midwif_pct` | percentage 0–100 | 24.9 | 99.5 | 0% sup |
| `average_out_of_pocket_expenditure_per_delivery_in_a_public_fac` | currency: INR | 193 | 2.01e+04 | 0% sup |
| `children_born_at_home_who_were_taken_to_a_health_facility_f_pct` | percentage 0–100 | 0 | 29 | 60% sup |
| `children_who_received_pnc_from_a_doctor_nurse_lhv_anm_midwi_pct` | percentage 0–100 | 22.4 | 99.6 | 0% sup |
| `institutional_birth_5y_pct` | percentage 0–100 | 21.4 | 100 | 0% sup |
| `institutional_birth_in_public_facility_5y_pct` | percentage 0–100 | 18.1 | 96.7 | 0% sup |
| `home_birth_that_were_conducted_by_skilled_hp_5y_10_pct` | percentage 0–100 | 0 | 19.9 | 0% sup |
| `births_attended_by_skilled_hp_5y_10_pct` | percentage 0–100 | 30.9 | 100 | 0% sup |
| `births_delivered_by_csection_5y_pct` | percentage 0–100 | 1.4 | 82.4 | 0% sup |
| `births_in_a_private_fac_that_were_delivered_by_csection_5y_pct` | percentage 0–100 | 6.3 | 94.2 | 21% sup |
| `births_in_a_public_fac_that_were_delivered_by_csection_5y_pct` | percentage 0–100 | 0.7 | 73 | 0% sup |
| `child_12_23m_fully_vaccinated_based_on_information_from_eit_pct` | percentage 0–100 | 38.3 | 100 | 2% sup |
| `child_12_23m_fully_vaccinated_based_on_information_from_vax_pct` | percentage 0–100 | 45 | 100 | 3% sup |
| `child_12_23m_who_have_received_bcg_pct` | percentage 0–100 | 65.9 | 100 | 2% sup |
| `child_12_23m_who_have_received_3_doses_of_polio_vaccine_pct` | percentage 0–100 | 47.6 | 100 | 2% sup |
| `child_12_23m_who_have_received_3_doses_of_penta_or_dpt_vacc_pct` | percentage 0–100 | 53.3 | 100 | 2% sup |
| `child_12_23m_who_have_received_the_first_dose_of_mcv_mcv_pct` | percentage 0–100 | 53.2 | 100 | 2% sup |
| `child_24_35m_who_have_received_a_second_dose_of_mcv_mcv_pct` | percentage 0–100 | 2.8 | 63.8 | 2% sup |
| `child_12_23m_who_have_received_3_doses_of_rotavirus_vaccine_pct` | percentage 0–100 | 0 | 100 | 2% sup |
| `child_12_23m_who_have_received_3_doses_of_penta_or_hepatiti_pct` | percentage 0–100 | 39.5 | 100 | 2% sup |
| `child_9_35m_who_received_a_vit_a_in_the_last_6_months_pct` | percentage 0–100 | 27.5 | 98.1 | 0% sup |
| `child_12_23m_who_received_most_of_their_vaccinations_in_a_p_pct` | percentage 0–100 | 67.1 | 100 | 2% sup |
| `child_12_23m_who_received_most_of_their_vaccinations_in_a_2_pct` | percentage 0–100 | 0 | 32.9 | 2% sup |
| `prev_diarrhoea_2wk_child_u5_pct` | percentage 0–100 | 0 | 39.3 | 0% sup |
| `children_with_diarrhoea_2wk_who_received_oral_rehydration_s_pct` | percentage 0–100 | 18.8 | 95.9 | 70% sup |
| `children_with_diarrhoea_2wk_who_received_zinc_child_u5_pct` | percentage 0–100 | 4.2 | 70.4 | 70% sup |
| `children_with_diarrhoea_2wk_taken_to_a_health_facility_or_h_pct` | percentage 0–100 | 27.4 | 95.3 | 70% sup |
| `children_prev_symptoms_of_acute_respiratory_infection_ari_2_pct` | percentage 0–100 | 0 | 11.2 | 0% sup |
| `children_with_fever_or_symptoms_of_ari_2wk_taken_to_a_healt_pct` | percentage 0–100 | 13.8 | 97.3 | 32% sup |
| `children_under_age_3_years_breastfed_within_one_hour_of_bir_pct` | percentage 0–100 | 7.8 | 88.5 | 0% sup |
| `child_u6m_exclusively_breastfed_pct` | percentage 0–100 | 22.3 | 94 | 37% sup |
| `child_6_8m_receiving_solid_or_semi_solid_food_and_breastmil_pct` | percentage 0–100 | 7.9 | 85.2 | 91% sup |
| `breastfeeding_child_6_23m_receiving_an_adequate_diet16_17_pct` | percentage 0–100 | 0 | 54.1 | 1% sup |
| `non_breastfeeding_child_6_23m_receiving_an_adequate_diet16_pct` | percentage 0–100 | 0 | 41.3 | 91% sup |
| `total_child_6_23m_receiving_an_adequate_diet16_17_pct` | percentage 0–100 | 0 | 50.1 | 0% sup |
| `child_u5_who_are_stunted_height_for_age_18_pct` | percentage 0–100 | 13.2 | 60.6 | 0% sup |
| `child_u5_who_are_wasted_weight_for_height_18_pct` | percentage 0–100 | 4.5 | 48 | 0% sup |
| `child_u5_who_are_severe_wasted_weight_for_height_19_pct` | percentage 0–100 | 0.5 | 30.5 | 0% sup |
| `child_u5_who_are_underweight_weight_for_age_18_pct` | percentage 0–100 | 7.2 | 62.4 | 0% sup |
| `child_u5_who_are_overweight_weight_for_height_20_pct` | percentage 0–100 | 0 | 21.1 | 0% sup |
| `women_age_15_49_years_whose_bmi_bmi_is_underweight_bmi_lt_1_pct` | percentage 0–100 | 1.2 | 43.6 | 0% sup |
| `women_age_15_49_years_who_are_overweight_obese_bmi_gte_25_0_pct` | percentage 0–100 | 3.8 | 53 | 0% sup |
| `women_age_15_49_years_who_have_high_risk_whr_gte_0_85_pct` | percentage 0–100 | 18 | 96.6 | 0% sup |
| `child_6_59m_who_are_anaemic_lt_11_0_g_dl_22_pct` | percentage 0–100 | 24.9 | 95.5 | 0% sup |
| `non_pregnant_w15_49_who_are_anaemic_lt_12_0_g_dl_22_pct` | percentage 0–100 | 15.6 | 94.6 | 0% sup |
| `pregnant_w15_49_who_are_anaemic_lt_11_0_g_dl_22_pct` | percentage 0–100 | 2 | 87.6 | 19% sup |
| `all_w15_49_who_are_anaemic_pct` | percentage 0–100 | 14.9 | 93.5 | 0% sup |
| `all_w15_19_who_are_anaemic_pct` | percentage 0–100 | 18.2 | 97.1 | 0% sup |
| `women_age_15_years_and_above_with_high_141_160_mg_dl_blood_pct` | percentage 0–100 | 1.6 | 14.6 | 0% sup |
| `w15_plus_with_very_high_gt_160_mg_dl_blood_sugar_pct` | percentage 0–100 | 0.7 | 18 | 0% sup |
| `w15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct` | percentage 0–100 | 4.1 | 32.1 | 0% sup |
| `m15_plus_with_high_141_160_mg_dl_blood_sugar_pct` | percentage 0–100 | 1.7 | 18.3 | 0% sup |
| `men_age_15_years_and_above_with_very_high_gt_160_mg_dl_bloo_pct` | percentage 0–100 | 0.5 | 21.1 | 0% sup |
| `m15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct` | percentage 0–100 | 4.8 | 36.2 | 0% sup |
| `w15_plus_with_mildly_high_bp_sys_140_159_mmhg_and_or_dia_90_pct` | percentage 0–100 | 4.3 | 23.7 | 0% sup |
| `w15_plus_with_moderately_or_severely_high_bp_sys_gte_160_mm_pct` | percentage 0–100 | 0.7 | 15.8 | 0% sup |
| `w15_plus_with_high_bp_sys_gte_140_mmhg_and_or_dia_gte_90_mm_pct` | percentage 0–100 | 8.5 | 42.1 | 0% sup |
| `m15_plus_with_mildly_high_bp_sys_140_159_mmhg_and_or_dia_90_pct` | percentage 0–100 | 5.3 | 32.9 | 0% sup |
| `m15_plus_with_moderately_or_severely_high_bp_sys_gte_160_mm_pct` | percentage 0–100 | 0.8 | 19.5 | 0% sup |
| `m15_plus_with_high_bp_sys_gte_140_mmhg_and_or_dia_gte_90_mm_pct` | percentage 0–100 | 10 | 49.6 | 0% sup |
| `women_age_30_49_years_ever_undergone_a_cervical_screen_pct` | percentage 0–100 | 0 | 23.2 | 0% sup |
| `women_age_30_49_years_ever_undergone_a_breast_exam_pct` | percentage 0–100 | 0 | 14.6 | 0% sup |
| `women_age_30_49_years_ever_undergone_an_oral_cancer_exam_pct` | percentage 0–100 | 0 | 15.8 | 0% sup |
| `w15_plus_who_use_any_kind_of_tobacco_pct` | percentage 0–100 | 0.1 | 70.6 | 0% sup |
| `m15_plus_who_use_any_kind_of_tobacco_pct` | percentage 0–100 | 6.8 | 80.6 | 0% sup |
| `w15_plus_who_consume_alcohol_pct` | percentage 0–100 | 0 | 42.8 | 0% sup |
| `m15_plus_who_consume_alcohol_pct` | percentage 0–100 | 0.1 | 68.4 | 0% sup |
