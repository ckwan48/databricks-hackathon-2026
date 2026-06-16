## Consolidated Data Dictionary — every column & its meaning

*Plain-English meaning of all 171 columns across the three tables. NFHS meanings are derived from the indicator names + NFHS-5 conventions (denominator = the population the % is computed over); see the thematic NFHS sections for fuller definitions.*


### india_pincode.csv (11)
| # | Column | Meaning | Type |
|---|---|---|---|
| 0 | `circlename` | India Post Circle — top admin unit (≈ state level) | text |
| 1 | `regionname` | Postal Region — a group of divisions | text |
| 2 | `divisionname` | Postal Division — a group of post offices | text |
| 3 | `officename` | Name of the post office | text |
| 4 | `pincode` | 6-digit PIN: d1=region, d1–2=circle, d1–3=sorting district, last 3=delivery office | text |
| 5 | `officetype` | Office type HO/SO/BO (here all BO = Branch Office) | text |
| 6 | `delivery` | Whether the office performs delivery | text |
| 7 | `district` | Revenue district | text |
| 8 | `statename` | State / UT | text |
| 9 | `latitude` | Office latitude (some NA) | geo |
| 10 | `longitude` | Office longitude (some NA) | geo |

### facilities.csv (51)
| # | Column | Meaning | Type |
|---|---|---|---|
| 0 | `unique_id` | Surrogate primary key (UUID) of the scraped record | field |
| 1 | `source_types` | Provenance tag per evidence item (overture/dynamic/constant/mongo_facility) | json[] |
| 2 | `source_ids` | Source-record IDs, parallel to source_types | json[] |
| 3 | `source_content_id` | FK to upstream source-content record (==content_table_id) | field |
| 4 | `name` | Facility name | field |
| 5 | `organization_type` | Record class (always 'facility') | field |
| 6 | `content_table_id` | FK to content table (==source_content_id) | field |
| 7 | `phone_numbers` | All discovered phone numbers | json[] |
| 8 | `officialPhone` | Primary/official phone | field |
| 9 | `email` | Contact email | field |
| 10 | `websites` | All discovered URLs (site + social) | json[] |
| 11 | `officialWebsite` | Primary official website | field |
| 12 | `yearEstablished` | Year founded | field |
| 13 | `acceptsVolunteers` | Flag — accepts volunteers | field |
| 14 | `facebookLink` | Facebook URL | field |
| 15 | `address_line1` | Street address line 1 | field |
| 16 | `address_line2` | Street address line 2 | field |
| 17 | `address_line3` | Street address line 3 | field |
| 18 | `address_city` | City (often a town/district) | field |
| 19 | `address_stateOrRegion` | State (sometimes a district mis-filed) | field |
| 20 | `address_zipOrPostcode` | 6-digit PIN (FK → pincode) | field |
| 21 | `address_country` | Country | field |
| 22 | `address_countryCode` | ISO country code | field |
| 23 | `countries` | Country list | json[] |
| 24 | `facilityTypeId` | Facility class (hospital/clinic/dentist/doctor/farmacy) | field |
| 25 | `operatorTypeId` | Ownership (private/public) | field |
| 26 | `affiliationTypeIds` | Affiliation/accreditation IDs | json[] |
| 27 | `description` | Free-text summary | field |
| 28 | `area` | Locality / area name | field |
| 29 | `numberDoctors` | Reported number of doctors | field |
| 30 | `capacity` | Reported bed capacity | field |
| 31 | `specialties` | Clinical specialty codes (164-term taxonomy) | json[] |
| 32 | `procedure` | Procedure/service statements | json[] |
| 33 | `equipment` | Equipment statements | json[] |
| 34 | `capability` | Capability/claim statements | json[] |
| 35 | `recency_of_page_update` | Recency signal of the source page | field |
| 36 | `distinct_social_media_presence_count` | # distinct social platforms | field |
| 37 | `affiliated_staff_presence` | Flag — named staff present | field |
| 38 | `custom_logo_presence` | Flag — has a custom logo | field |
| 39 | `number_of_facts_about_the_organization` | # structured facts extracted | field |
| 40 | `post_metrics_most_recent_social_media_post_date` | Date of latest social post | field |
| 41 | `post_metrics_post_count` | # social posts | field |
| 42 | `engagement_metrics_n_followers` | Social followers | field |
| 43 | `engagement_metrics_n_likes` | Social likes | field |
| 44 | `engagement_metrics_n_engagements` | Social engagements | field |
| 45 | `source` | Pipeline source (always 'kie') | field |
| 46 | `coordinates` | GeoJSON point {coordinates:[lon,lat]} | geo |
| 47 | `latitude` | Latitude (some corrupt/out-of-India) | geo |
| 48 | `longitude` | Longitude (some corrupt/out-of-India) | geo |
| 49 | `cluster_id` | Entity-resolution key (dedupe across sources) | field |
| 50 | `source_urls` | Source page URLs | json[] |

### nfhs.csv (109)
| # | Column | Meaning | Denominator | Unit |
|---|---|---|---|---|
| 0 | `district_name` | District name (identifier) | — | id |
| 1 | `state_ut` | State / UT (identifier) | — | id |
| 2 | `households_surveyed` | Households surveyed (sample size) | households | count |
| 3 | `women_15_49_interviewed` | Women 15–49 interviewed (sample size) | women 15–49 | count |
| 4 | `men_15_54_interviewed` | Men 15–54 interviewed (sample size) | men 15–54 | count |
| 5 | `female_population_age_6_years_and_above_ever_schooled_pct` | Female population age 6 years and above ever schooled | — | % |
| 6 | `population_below_age_15_years_pct` | Population below age 15 years | — | % |
| 7 | `sex_ratio_total_f_per_1000_m` | Sex ratio total f per 1000 m | — | F per 1000 M |
| 8 | `sex_ratio_at_birth_5y_f_per_1000_m` | Sex ratio at birth 5y f per 1000 m | — | F per 1000 M |
| 9 | `child_u5_whose_birth_was_civil_reg_pct` | Whose birth was civil reg | children under 5 | % |
| 10 | `deaths_in_the_last_3_years_civil_reg_pct` | Deaths in the last 3 years civil reg | — | % |
| 11 | `hh_electricity_pct` | Hh electricity | households | % |
| 12 | `hh_improved_water_pct` | Hh improved water | households | % |
| 13 | `hh_use_improved_sanitation_pct` | Hh use improved sanitation | households | % |
| 14 | `households_using_clean_fuel_for_cooking_pct` | Households using clean fuel for cooking | households | % |
| 15 | `households_using_iodized_salt_pct` | Households using iodized salt | households | % |
| 16 | `hh_member_covered_health_insurance_pct` | Hh member covered health insurance | households | % |
| 17 | `child_5y_who_attended_pre_primary_school_during_the_school_pct` | Child 5y who attended pre primary school during the school | — | % |
| 18 | `women_age_15_49_who_are_literate_pct` | Who are literate | women 15–49 | % |
| 19 | `women_age_15_49_with_10_or_more_years_of_schooling_pct` | With 10 or more years of schooling | women 15–49 | % |
| 20 | `w20_24_married_before_age_18_years_pct` | Married before age 18 years | women 20–24 | % |
| 21 | `births_in_the_5_years_preceding_the_survey_that_are_birth_3_pct` | Births in the 5 years preceding the survey that are birth | births in last 5 years | % |
| 22 | `w15_19_who_were_already_mothers_or_pregnant_at_the_time_of_pct` | Who were already mothers or pregnant at the time of | women/girls 15–19 | % |
| 23 | `w15_24_who_use_menstrual_hygiene_pct` | Who use menstrual hygiene | young women 15–24 | % |
| 24 | `fp_cm_w15_49_any_method_pct` | Family planning — any method | currently married women 15–49 | % |
| 25 | `fp_cm_w15_49_modern_method_pct` | Family planning — modern method | currently married women 15–49 | % |
| 26 | `fp_cm_w15_49_f_steril_pct` | Family planning — female sterilisation | currently married women 15–49 | % |
| 27 | `fp_cm_w15_49_m_steril_pct` | Family planning — male sterilisation | currently married women 15–49 | % |
| 28 | `fp_cm_w15_49_iud_pct` | Family planning — iud | currently married women 15–49 | % |
| 29 | `fp_cm_w15_49_pill_pct` | Family planning — pill | currently married women 15–49 | % |
| 30 | `fp_cm_w15_49_condom_pct` | Family planning — condom | currently married women 15–49 | % |
| 31 | `fp_cm_w15_49_injectables_pct` | Family planning — injectables | currently married women 15–49 | % |
| 32 | `fp_unmet_total_cm_w15_49_7_pct` | Unmet need for family planning — total cm | women 15–49 | % |
| 33 | `fp_unmet_spacing_cm_w15_49_7_pct` | Unmet need for family planning — spacing cm | women 15–49 | % |
| 34 | `health_worker_ever_talked_to_female_non_users_about_family_pct` | Health worker ever talked to female non users about family | — | % |
| 35 | `current_users_ever_told_about_side_effects_of_current_metho_pct` | Current users ever told about side effects of current metho | — | % |
| 36 | `mothers_who_had_an_anc_visit_in_the_first_trimester_lb5y_pct` | Mothers who had an ANC visit in the first trimester lb5y | mothers (last birth in 5y) | % |
| 37 | `mothers_who_had_at_least_4_anc_visits_lb5y_pct` | Mothers who had at least 4 ANC visits lb5y | mothers (last birth in 5y) | % |
| 38 | `mothers_whose_last_birth_was_protected_against_neo_tetanus_pct` | Mothers whose last birth was protected against neonatal tetanus | mothers (last birth in 5y) | % |
| 39 | `mothers_who_consumed_ifa_for_100_days_or_more_when_they_wer_pct` | Mothers who consumed iron-folic-acid for 100 days or more when they wer | mothers (last birth in 5y) | % |
| 40 | `mothers_who_consumed_ifa_for_180_days_or_more_when_they_wer_pct` | Mothers who consumed iron-folic-acid for 180 days or more when they wer | mothers (last birth in 5y) | % |
| 41 | `registered_pregnancies_for_which_the_mother_received_a_mcp_pct` | Registered pregnancies for which the mother received a MCP card | registered pregnancies | % |
| 42 | `mothers_who_received_pnc_from_a_doctor_nurse_lhv_anm_midwif_pct` | Mothers who received PNC from a doctor nurse lhv anm midwif | mothers (last birth in 5y) | % |
| 43 | `average_out_of_pocket_expenditure_per_delivery_in_a_public_fac` | Average out of pocket expenditure per delivery in a public fac | — | INR |
| 44 | `children_born_at_home_who_were_taken_to_a_health_facility_f_pct` | Children born at home who were taken to a health facility f | — | % |
| 45 | `children_who_received_pnc_from_a_doctor_nurse_lhv_anm_midwi_pct` | Children who received PNC from a doctor nurse lhv anm midwi | — | % |
| 46 | `institutional_birth_5y_pct` | Institutional birth 5y | — | % |
| 47 | `institutional_birth_in_public_facility_5y_pct` | Institutional birth in public facility 5y | — | % |
| 48 | `home_birth_that_were_conducted_by_skilled_hp_5y_10_pct` | Home birth that were conducted by skilled hp 5y | — | % |
| 49 | `births_attended_by_skilled_hp_5y_10_pct` | Births attended by skilled hp 5y | births in last 5 years | % |
| 50 | `births_delivered_by_csection_5y_pct` | Births delivered by C-section 5y | births in last 5 years | % |
| 51 | `births_in_a_private_fac_that_were_delivered_by_csection_5y_pct` | Births in a private fac that were delivered by C-section 5y | births in last 5 years | % |
| 52 | `births_in_a_public_fac_that_were_delivered_by_csection_5y_pct` | Births in a public fac that were delivered by C-section 5y | births in last 5 years | % |
| 53 | `child_12_23m_fully_vaccinated_based_on_information_from_eit_pct` | Fully vaccinated based on information from eit | children 12–23 months | % |
| 54 | `child_12_23m_fully_vaccinated_based_on_information_from_vax_pct` | Fully vaccinated based on information from vax | children 12–23 months | % |
| 55 | `child_12_23m_who_have_received_bcg_pct` | Who have received BCG | children 12–23 months | % |
| 56 | `child_12_23m_who_have_received_3_doses_of_polio_vaccine_pct` | Who have received 3 doses of polio vaccine | children 12–23 months | % |
| 57 | `child_12_23m_who_have_received_3_doses_of_penta_or_dpt_vacc_pct` | Who have received 3 doses of penta or DPT vacc | children 12–23 months | % |
| 58 | `child_12_23m_who_have_received_the_first_dose_of_mcv_mcv_pct` | Who have received the first dose of measles vaccine mcv | children 12–23 months | % |
| 59 | `child_24_35m_who_have_received_a_second_dose_of_mcv_mcv_pct` | Who have received a second dose of measles vaccine mcv | children 24–35 months | % |
| 60 | `child_12_23m_who_have_received_3_doses_of_rotavirus_vaccine_pct` | Who have received 3 doses of rotavirus vaccine | children 12–23 months | % |
| 61 | `child_12_23m_who_have_received_3_doses_of_penta_or_hepatiti_pct` | Who have received 3 doses of penta or hepatiti | children 12–23 months | % |
| 62 | `child_9_35m_who_received_a_vit_a_in_the_last_6_months_pct` | Who received a vitamin A in the last 6 months | children 9–35 months | % |
| 63 | `child_12_23m_who_received_most_of_their_vaccinations_in_a_p_pct` | Who received most of their vaccinations in a p | children 12–23 months | % |
| 64 | `child_12_23m_who_received_most_of_their_vaccinations_in_a_2_pct` | Who received most of their vaccinations in a | children 12–23 months | % |
| 65 | `prev_diarrhoea_2wk_child_u5_pct` | Prev diarrhoea 2wk | children under 5 | % |
| 66 | `children_with_diarrhoea_2wk_who_received_oral_rehydration_s_pct` | Children with diarrhoea 2wk who received oral rehydration s | — | % |
| 67 | `children_with_diarrhoea_2wk_who_received_zinc_child_u5_pct` | Children with diarrhoea 2wk who received zinc | children under 5 | % |
| 68 | `children_with_diarrhoea_2wk_taken_to_a_health_facility_or_h_pct` | Children with diarrhoea 2wk taken to a health facility or h | — | % |
| 69 | `children_prev_symptoms_of_acute_respiratory_infection_ari_2_pct` | Children prev symptoms of acute respiratory infection ARI | — | % |
| 70 | `children_with_fever_or_symptoms_of_ari_2wk_taken_to_a_healt_pct` | Children with fever or symptoms of ARI 2wk taken to a healt | — | % |
| 71 | `children_under_age_3_years_breastfed_within_one_hour_of_bir_pct` | Years breastfed within one hour of bir | children under 3 | % |
| 72 | `child_u6m_exclusively_breastfed_pct` | Exclusively breastfed | children under 6 months | % |
| 73 | `child_6_8m_receiving_solid_or_semi_solid_food_and_breastmil_pct` | Receiving solid or semi solid food and breastmil | children 6–8 months | % |
| 74 | `breastfeeding_child_6_23m_receiving_an_adequate_diet16_17_pct` | Breastfeeding receiving an adequate diet16 | children 6–23 months | % |
| 75 | `non_breastfeeding_child_6_23m_receiving_an_adequate_diet16_pct` | Non breastfeeding receiving an adequate diet16 | children 6–23 months | % |
| 76 | `total_child_6_23m_receiving_an_adequate_diet16_17_pct` | Total receiving an adequate diet16 | children 6–23 months | % |
| 77 | `child_u5_who_are_stunted_height_for_age_18_pct` | Who are stunted height for age | children under 5 | % |
| 78 | `child_u5_who_are_wasted_weight_for_height_18_pct` | Who are wasted weight for height | children under 5 | % |
| 79 | `child_u5_who_are_severe_wasted_weight_for_height_19_pct` | Who are severe wasted weight for height | children under 5 | % |
| 80 | `child_u5_who_are_underweight_weight_for_age_18_pct` | Who are underweight weight for age | children under 5 | % |
| 81 | `child_u5_who_are_overweight_weight_for_height_20_pct` | Who are overweight weight for height | children under 5 | % |
| 82 | `women_age_15_49_years_whose_bmi_bmi_is_underweight_bmi_lt_1_pct` | Years whose bmi bmi is underweight bmi < | women 15–49 | % |
| 83 | `women_age_15_49_years_who_are_overweight_obese_bmi_gte_25_0_pct` | Years who are overweight obese bmi gte 25 | women 15–49 | % |
| 84 | `women_age_15_49_years_who_have_high_risk_whr_gte_0_85_pct` | Years who have high risk whr gte 0 | women 15–49 | % |
| 85 | `child_6_59m_who_are_anaemic_lt_11_0_g_dl_22_pct` | Who are anaemic < 11 0 g/dl | children 6–59 months | % |
| 86 | `non_pregnant_w15_49_who_are_anaemic_lt_12_0_g_dl_22_pct` | Who are anaemic < 12 0 g/dl | non-pregnant women 15–49 | % |
| 87 | `pregnant_w15_49_who_are_anaemic_lt_11_0_g_dl_22_pct` | Who are anaemic < 11 0 g/dl | pregnant women 15–49 | % |
| 88 | `all_w15_49_who_are_anaemic_pct` | All who are anaemic | women 15–49 | % |
| 89 | `all_w15_19_who_are_anaemic_pct` | All who are anaemic | women/girls 15–19 | % |
| 90 | `women_age_15_years_and_above_with_high_141_160_mg_dl_blood_pct` | With high 141 160 mg/dl blood | women 15+ | % |
| 91 | `w15_plus_with_very_high_gt_160_mg_dl_blood_sugar_pct` | With very high > 160 mg/dl blood sugar | women 15+ | % |
| 92 | `w15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct` | With high or very high > 140 mg/dl blood sugar or | women 15+ | % |
| 93 | `m15_plus_with_high_141_160_mg_dl_blood_sugar_pct` | With high 141 160 mg/dl blood sugar | men 15+ | % |
| 94 | `men_age_15_years_and_above_with_very_high_gt_160_mg_dl_bloo_pct` | With very high > 160 mg/dl bloo | men 15+ | % |
| 95 | `m15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct` | With high or very high > 140 mg/dl blood sugar or | men 15+ | % |
| 96 | `w15_plus_with_mildly_high_bp_sys_140_159_mmhg_and_or_dia_90_pct` | With mildly high blood pressure sys 140 159 mmhg and or dia | women 15+ | % |
| 97 | `w15_plus_with_moderately_or_severely_high_bp_sys_gte_160_mm_pct` | With moderately or severely high blood pressure sys gte 160 mm | women 15+ | % |
| 98 | `w15_plus_with_high_bp_sys_gte_140_mmhg_and_or_dia_gte_90_mm_pct` | With high blood pressure sys gte 140 mmhg and or dia gte 90 mm | women 15+ | % |
| 99 | `m15_plus_with_mildly_high_bp_sys_140_159_mmhg_and_or_dia_90_pct` | With mildly high blood pressure sys 140 159 mmhg and or dia | men 15+ | % |
| 100 | `m15_plus_with_moderately_or_severely_high_bp_sys_gte_160_mm_pct` | With moderately or severely high blood pressure sys gte 160 mm | men 15+ | % |
| 101 | `m15_plus_with_high_bp_sys_gte_140_mmhg_and_or_dia_gte_90_mm_pct` | With high blood pressure sys gte 140 mmhg and or dia gte 90 mm | men 15+ | % |
| 102 | `women_age_30_49_years_ever_undergone_a_cervical_screen_pct` | Years ever undergone a cervical screen | women 30–49 | % |
| 103 | `women_age_30_49_years_ever_undergone_a_breast_exam_pct` | Years ever undergone a breast exam | women 30–49 | % |
| 104 | `women_age_30_49_years_ever_undergone_an_oral_cancer_exam_pct` | Years ever undergone an oral cancer exam | women 30–49 | % |
| 105 | `w15_plus_who_use_any_kind_of_tobacco_pct` | Who use any kind of tobacco | women 15+ | % |
| 106 | `m15_plus_who_use_any_kind_of_tobacco_pct` | Who use any kind of tobacco | men 15+ | % |
| 107 | `w15_plus_who_consume_alcohol_pct` | Who consume alcohol | women 15+ | % |
| 108 | `m15_plus_who_consume_alcohol_pct` | Who consume alcohol | men 15+ | % |
