## Complete Unique-Values Catalog (every column, every table)

*Categorical (≤30 unique): full value list with counts. Numeric: cardinality + range (continuous, not enumerable). JSON-array: distinct token count + top tokens. ID/high-card: cardinality + examples.*

### india_pincode.csv — 165627 rows × 11 columns

| # | Column | Kind | Fill | #unique | Values / range |
|---|---|---|---|---|---|
| 0 | `circlename` | categorical | 100% | 24 | Uttar Pradesh Circle (17997); Maharashtra Circle (14073); Tamilnadu Circle (11839); Rajasthan Circle (11053); Andhra Pradesh Circle (10686); Madhya Pradesh Circle (10292); Karnataka Circle (9670); Bihar Circle (9369); West Bengal Circle (9109); Odisha Circle (8920); Gujarat Circle (8905); Telangana Circle (6304); Kerala Circle (5080); Chattisgarh Circle (4770); Jharkhand Circle (4599); North Eastern Circle (4477); Assam Circle (4070); Punjab Circle (3852); Himachal Pradesh Circle (2811); Uttarakhand Circle (2741); Haryana Circle (2717); Jammu Kashmir Circle (1740); Delhi Circle (551); APS CIRCLE (2) |
| 1 | `regionname` | id/high-card | 100% | 52 | e.g. Hyderabad Region; Hyderabad City Reg; Vijayawada Region … |
| 2 | `divisionname` | id/high-card | 100% | 482 | e.g. Adilabad Division; Hanamkonda Divisio; Karimnagar Divisio … |
| 3 | `officename` | id/high-card | 100% | 145086 | e.g. Kothimir B.O; Papanpet B.O; Kukuda B.O … |
| 4 | `pincode` | id | 100% | 19586 | e.g. 504273, 504299, 504296 … |
| 5 | `officetype` | categorical | 100% | 3 | BO (140270); PO (24546); HO (811) |
| 6 | `delivery` | categorical | 100% | 2 | Delivery (157901); Non Delivery (7726) |
| 7 | `district` | id/high-card | 100% | 749 | e.g. KUMURAM BHEEM ASIF; MANCHERIAL; HANUMAKONDA … |
| 8 | `statename` | id/high-card | 100% | 36 | e.g. TELANGANA; ANDHRA PRADESH; ASSAM … |
| 9 | `latitude` | numeric | 93% | 99918 | min 0 · median 22.77 · max 2.336e+08 |
| 10 | `longitude` | numeric | 93% | 94867 | min 0 · median 78.86 · max 9.335e+09 |

### facilities.csv — 10088 rows × 51 columns

| # | Column | Kind | Fill | #unique | Values / range |
|---|---|---|---|---|---|
| 0 | `unique_id` | id/high-card | 100% | 10077 | e.g. b8a5401f-42f1-422a; 06d5fb63-b2f1-4001; 29b6dbe0-f471-4650 … |
| 1 | `source_types` | json[] | 99% | 6312 | 5 tokens; top: overture×162020, dynamic×82952, constant×20669, mongo_facility×5955, mongo_ngo×1121 |
| 2 | `source_ids` | json[] | 99% | 9261 | 29356 tokens; top: 08f694ec74a81d800351cfba3f69ee2c×263, 08f8b2c8840802c203e185dde420525c×262, 08f3cccd4c9316800364b8e98d455189×261, 08f3cb1caa6aa908030b6e7d488d32ed×208, 08f3c9c06035213603358c65ab3762fb×184, 08f6933d92031775030348d76914426e×177 |
| 3 | `source_content_id` | id/high-card | 99% | 9086 | e.g. c2ada12b-11f7-45f2; a3168d54-bc65-4ebc; 39dd607d-6956-44f2 … |
| 4 | `name` | id/high-card | 99% | 9530 | e.g. Aravind Eye Hospit; Fortis Hospital, G; Fortis Hospital An … |
| 5 | `organization_type` | categorical | 99% | 28 | facility (10000);  Doctor couple's unblemish (1); ["The Child Care Centre pa (1);  Chennai.   (1);  MGR University (1); ["Performs In Vitro Fertil (1);  no less than (1); ["MDCT Scan service","Digi (1);  who extended their hand i (1); ["radiology","cardiology", (1);  17 bedded Dialysis Unit a (1); ["reproductiveEndocrinolog (1); ""glaucomaOphthalmology"" (1); 100 (1);  and hair loss (1); 50 (1); ["dentistry","dentistry"," (1); ["Provides magnetic resona (1); ["Performs blood testing", (1); ["Performs retinal surgeri (1); ["Udwartanam (Powder Massa (1); ["Aortic Aneurysm Repair", (1); ["Performs echocardiograph (1);  dental implants (1); ["orthodontics","dentistry (1); ["dentistry","endodontics" (1); ["familyMedicine","dentist (1);  PCOD (1) |
| 6 | `content_table_id` | id/high-card | 99% | 9092 | e.g. c2ada12b-11f7-45f2; a3168d54-bc65-4ebc; 39dd607d-6956-44f2 … |
| 7 | `phone_numbers` | json[] | 97% | 9729 | 37456 tokens; top: +919693969347×708, +918001031041×383, +9118001031041×168, +918049388781×168, +9118003092323×149, +917406499999×130 |
| 8 | `officialPhone` | numeric | 94% | 9176 | min 100 · median 9.184e+11 · max 9.118e+14 |
| 9 | `email` | id/high-card | 85% | 8065 | e.g. ighofficedwarka@gm; [email protected]; appointment@tmckol … |
| 10 | `websites` | json[] | 99% | 10008 | 121033 tokens; top: indiraivf.in×139, novaivffertility.com×105, hcgoncology.com×96, apollohospitals.com×94, redcliffelabs.com×91, maxlab.co.in×90 |
| 11 | `officialWebsite` | id/high-card | 83% | 8015 | e.g. aravind.org; fortishealthcare.c; tmckolkata.com … |
| 12 | `yearEstablished` | id/high-card | 48% | 157 | e.g. 1991; 2001; 2011 … |
| 13 | `acceptsVolunteers` | categorical | 0% | 16 | true (21); false (7); 2020-05-23 (1); 2020-06-10 (1); 2022-09-29 (1); ["Oberoi Hospital is locat (1); 2024-08-22 (1); 3 (1); 6 (1); ""urology"" (1); 1 (1); 2025-01-23 (1); 2022-12-24 (1); 2023-04-13 (1); ",null,null,null,"[""denti (1); ["Wheelchair accessibility (1) |
| 14 | `facebookLink` | id/high-card | 98% | 9880 | e.g. https://www.facebo; https://www.facebo; https://www.facebo … |
| 15 | `address_line1` | id/high-card | 99% | 9671 | e.g. Santosh Nagar Colo; Sector 44; 8/3, Alipur Road … |
| 16 | `address_line2` | id/high-card | 97% | 8900 | e.g. Delhi Gate; Opposite Huda City; Anandapur, East Ko … |
| 17 | `address_line3` | id/high-card | 70% | 6058 | e.g. Delhi Gate; Sector - 41; New Town Action Ar … |
| 18 | `address_city` | id/high-card | 99% | 1642 | e.g. Hyderabad; Gurgaon; Kolkata … |
| 19 | `address_stateOrRegion` | id/high-card | 99% | 253 | e.g. Telangana; Haryana; West Bengal … |
| 20 | `address_zipOrPostcode` | numeric | 99% | 3216 | min 0 · median 4.111e+05 · max 5.6e+06 |
| 21 | `address_country` | categorical | 99% | 28 | India (10000); kie (3); 524 (1); 80.35516357421875 (1); 80.26488494873047 (1); 45 (1); 72.96014404296875 (1); 74 (1); 12.916261672973633 (1); 23.170246124267578 (1); ""ophthalmology"" (1); {"coordinates":[75.7204513 (1); 0 (1); 5 (1); {"coordinates":[74.9095611 (1); 25.620325088500977 (1); 76.98989868164062 (1); 75.90425109863281 (1); 78.47290802001953 (1); 77.3935546875 (1); 82.9600601196289 (1); {"coordinates":[77.5779418 (1); 77.3350830078125 (1); {"coordinates":[79.5846710 (1); ["Equipped with the latest (1); 28.655179977416992 (1); 8.182075500488281 (1); 17.483631134033203 (1) |
| 22 | `address_countryCode` | categorical | 99% | 29 | IN (10000); kie (2); 1 (1); 0029c85a-fa3b-45a7-b892-3f (1); 08f618c4f699aad403056533b3 (1); 0 (1); 08f42ce2cd05400103fcae21e7 (1); {"coordinates":[85.1504974 (1); 80.19386291503906 (1); {"coordinates":[75.7541351 (1); 88.55764770507812 (1); ""internalMedicine"" (1); 29.146865844726562 (1); true (1); 31.616241455078125 (1); 85.12193298339844 (1); 08f603386160025803f0684c31 (1); {"coordinates":[85.7743911 (1); 08f3d16595b30b840312e224af (1); 08f60a25b314584103e2f865a4 (1); 08f3da1a4b08a4d8039c2e4760 (1); 04f6cb40-4689-4492-9cdc-b1 (1); 12.92794132232666 (1); 08f3da106062c2cb03eb85cf1b (1); 17.999603271484375 (1); ["Adheres to strict intern (1); 77.35955047607422 (1); 77.43661499023438 (1); 78.3896255493164 (1) |
| 23 | `countries` | json[] | 0% | 28 | 90 tokens; top: coordinates×2, type×2, https://www.justdial.com/Ghaziabad/Dr-Umesh-Srivastava-Apollo-Clinic-Raj-Nagar-Ghaziabad/011PXX11-XX11-191001191119-S3J2_BZDET/amp×1, https://www.vyapaaradda.com/dr-ashish-prakash-mbbs-md-dnb-mother-and-child-care-at-ghaziabad-651303460a68b×1, https://www.lkouniv.ac.in/en/page/child-care-center×1, https://www.facebook.com/352600375136073×1 |
| 24 | `facilityTypeId` | categorical | 99% | 26 | hospital (5637); clinic (3782); dentist (490); doctor (21); farmacy (10); pharmacy (2); {"coordinates":[80.9906845 (1); kie (1); 85.15049743652344 (1); 21.083206176757812 (1); ["https://venkateswaradiag (1); nursing_home (1); 75.75413513183594 (1); ["https://www.manoramahosp (1); ""cataractAndAnteriorSegme (1); 08f3da5d5e468b2a03d47c01e6 (1); 23.013490676879883 (1); 08f3d32534cd998d03b0bda3b1 (1); ["https://mediniz.com/publ (1); 85.7743911743164 (1); 08f6189259aa5742032b548fbd (1); 08f60b0952d93041035b12518b (1); 6 (1); ["https://www.drvaibhavjos (1); ["https://www.drbasdentalc (1); ["https://www.1mg.com/doct (1) |
| 25 | `operatorTypeId` | categorical | 92% | 17 | private (8842); public (469); government (2); 26.885332107543945 (1); {"coordinates":[75.5718994 (1); 00e60e06-25ed-43b3-a5fd-e3 (1); 81.65721130371094 (1); 08f3d9666086a7a90355f64c2d (1); ""retinaAndVitreoretinalOp (1); ["https://www.justdial.com (1); 72.52645111083984 (1); ["https://www.justdial.com (1); 08f3c8e4161710a00303e18d2c (1); ["https://sbayurvedahospit (1); ["https://www.justdial.com (1); true (1); kie (1) |
| 26 | `affiliationTypeIds` | json[] | 12% | 307 | 53 tokens; top: government×3342, academic×1820, philanthropy-legacy×330, faith-tradition×244, community×130, private×20 |
| 27 | `description` | id/high-card | 99% | 9577 | e.g. Referral hospital ; Fortis Memorial Re; Listed as an affil … |
| 28 | `area` | id/high-card | 1% | 97 | e.g. 20000; 1000; 22337 … |
| 29 | `numberDoctors` | id/high-card | 36% | 170 | e.g. 1; 200; 105 … |
| 30 | `capacity` | id/high-card | 25% | 315 | e.g. 650; 1000; 437 … |
| 31 | `specialties` | json[] | 99% | 9662 | 2935 tokens; top: internalMedicine×68026, familyMedicine×23732, dentistry×13111, gynecologyAndObstetrics×11020, ophthalmology×7645, orthopedicSurgery×7278 |
| 32 | `procedure` | json[] | 99% | 8815 | 89193 tokens; top: ×3628, Dental implants×398, Dental Implants×364, Root canal treatment×332, Laparoscopic surgery×293, Root Canal Treatment×281 |
| 33 | `equipment` | json[] | 98% | 6892 | 35144 tokens; top: ×4075, CT scanner×693, MRI scanner×419, Wheelchair accessible entrance and exit×395, Wheelchair-accessible entrance and exit×331, X-ray imaging equipment×304 |
| 34 | `capability` | json[] | 99% | 9921 | 168161 tokens; top: ×833, Outpatient dental clinic×662, NABH accredited×599, 24/7 emergency care×557, Provides 24/7 emergency care×534, Operates 24/7×533 |
| 35 | `recency_of_page_update` | id/high-card | 35% | 873 | e.g. 2027-07-20; 2025-12-13; 2025-12-20 … |
| 36 | `distinct_social_media_presence_count` | categorical | 99% | 13 | 5 (2737); 1 (1917); 3 (1677); 4 (1284); 2 (892); 6 (715); 0 (434); 9 (149); 7 (107); 8 (50); 11 (2); 79.52578735351562 (1); 10 (1) |
| 37 | `affiliated_staff_presence` | categorical | 99% | 4 | true (9260); false (697); 24 (1); 08f3dad0a384953403371415e0 (1) |
| 38 | `custom_logo_presence` | categorical | 95% | 4 | true (8611); false (998); 3 (1); ["https://bizeleven.com/li (1) |
| 39 | `number_of_facts_about_the_organization` | id/high-card | 27% | 52 | e.g. 73; 17; 11 … |
| 40 | `post_metrics_most_recent_social_media_post_date` | id/high-card | 49% | 2114 | e.g. 2025-12-17; 2025-11-14; 2025-12-14 … |
| 41 | `post_metrics_post_count` | id/high-card | 38% | 100 | e.g. 3; 4; 2 … |
| 42 | `engagement_metrics_n_followers` | numeric | 88% | 1321 | min 0 · median 244.5 · max 1.5e+07 |
| 43 | `engagement_metrics_n_likes` | id/high-card | 77% | 1031 | e.g. 4; 825; 37 … |
| 44 | `engagement_metrics_n_engagements` | id/high-card | 48% | 435 | e.g. 6; 12853; 9 … |
| 45 | `source` | categorical | 99% | 2 | kie (9970); 08f60a8951489ac003bda77daf (1) |
| 46 | `coordinates` | id/high-card | 99% | 9918 | e.g. {"coordinates":[79; {"coordinates":[77; {"coordinates":[88 … |
| 47 | `latitude` | numeric | 99% | 9891 | min -81.71 · median 22.28 · max 59.95 |
| 48 | `longitude` | numeric | 99% | 9796 | min -38.26 · median 77.13 · max 109.7 |
| 49 | `cluster_id` | id/high-card | 99% | 9959 | e.g. 000140e6-c506-4f6e; 00227b49-64f2-4a16; 0001a9c0-4c84-4535 … |
| 50 | `source_urls` | json[] | 99% | 9959 | 109501 tokens; top: https://www.medicineindia.org/hospitals-in-state/gujarat×80, https://www.medicineindia.org/hospitals-in-city/bangalore-karnataka×79, https://www.medicineindia.org/hospitals-in-state/uttar-pradesh×75, https://www.medicineindia.org/hospitals-in-state/haryana×71, http://www.healthinsuranceindia.org/cashless_hospital_india/maharashtra.html×67, https://khabarchhe.com/news-views/coronavirus/know-all-the-information-regarding-corona-vaccine×63 |

### nfhs.csv — 706 rows × 109 columns

| # | Column | Kind | Fill | #unique | Values / range |
|---|---|---|---|---|---|
| 0 | `district_name` | id/high-card | 100% | 698 | e.g. Nicobars; North & Middle And; South Andaman  … |
| 1 | `state_ut` | id/high-card | 100% | 36 | e.g. Andaman & Nicobar ; Andhra Pradesh; Arunachal Pradesh … |
| 2 | `households_surveyed` | numeric | 100% | 185 | min 213 · median 908 · max 990 |
| 3 | `women_15_49_interviewed` | numeric | 100% | 435 | min 216 · median 1020 · max 1621 |
| 4 | `men_15_54_interviewed` | numeric | 100% | 146 | min 17 · median 145 · max 241 |
| 5 | `female_population_age_6_years_and_above_ever_schooled_pct` | numeric | 100% | 336 | min 45.4 · median 71.35 · max 99.2 |
| 6 | `population_below_age_15_years_pct` | numeric | 100% | 206 | min 16 · median 25.4 · max 50.6 |
| 7 | `sex_ratio_total_f_per_1000_m` | numeric | 100% | 267 | min 755 · median 1013 · max 1332 |
| 8 | `sex_ratio_at_birth_5y_f_per_1000_m` | numeric | 100% | 351 | min 658 · median 932.5 · max 1485 |
| 9 | `child_u5_whose_birth_was_civil_reg_pct` | numeric | 100% | 239 | min 51.6 · median 94.85 · max 100 |
| 10 | `deaths_in_the_last_3_years_civil_reg_pct` | numeric | 100% | 452 | min 8.3 · median 76.2 · max 100 |
| 11 | `hh_electricity_pct` | numeric | 100% | 123 | min 68.4 · median 98.7 · max 100 |
| 12 | `hh_improved_water_pct` | numeric | 100% | 197 | min 41.2 · median 97 · max 100 |
| 13 | `hh_use_improved_sanitation_pct` | numeric | 100% | 380 | min 29.2 · median 73.75 · max 99.9 |
| 14 | `households_using_clean_fuel_for_cooking_pct` | numeric | 100% | 489 | min 8.6 · median 50.5 · max 99.8 |
| 15 | `households_using_iodized_salt_pct` | numeric | 100% | 166 | min 47.9 · median 97 · max 100 |
| 16 | `hh_member_covered_health_insurance_pct` | numeric | 100% | 470 | min 1.2 · median 35.7 · max 97.8 |
| 17 | `child_5y_who_attended_pre_primary_school_during_the_school_pct` | numeric | 100% | 362 | min 0 · median 9.6 · max 52.9 |
| 18 | `women_age_15_49_who_are_literate_pct` | numeric | 100% | 361 | min 38.6 · median 75.1 · max 99.7 |
| 19 | `women_age_15_49_with_10_or_more_years_of_schooling_pct` | numeric | 100% | 387 | min 13.6 · median 39.2 · max 88.2 |
| 20 | `w20_24_married_before_age_18_years_pct` | numeric | 100% | 356 | min 0 · median 18.25 · max 57.6 |
| 21 | `births_in_the_5_years_preceding_the_survey_that_are_birth_3_pct` | numeric | 100% | 70 | min 0 · median 1.8 · max 8 |
| 22 | `w15_19_who_were_already_mothers_or_pregnant_at_the_time_of_pct` | numeric | 100% | 171 | min 0 · median 4.8 · max 27.3 |
| 23 | `w15_24_who_use_menstrual_hygiene_pct` | numeric | 100% | 376 | min 9 · median 79.6 · max 100 |
| 24 | `fp_cm_w15_49_any_method_pct` | numeric | 100% | 344 | min 12.1 · median 68.1 · max 89.1 |
| 25 | `fp_cm_w15_49_modern_method_pct` | numeric | 100% | 375 | min 10.6 · median 55.6 · max 81.2 |
| 26 | `fp_cm_w15_49_f_steril_pct` | numeric | 100% | 442 | min 1.1 · median 34.15 · max 76.5 |
| 27 | `fp_cm_w15_49_m_steril_pct` | numeric | 100% | 54 | min 0 · median 0.1 · max 18.4 |
| 28 | `fp_cm_w15_49_iud_pct` | numeric | 100% | 106 | min 0 · median 1.9 · max 32.2 |
| 29 | `fp_cm_w15_49_pill_pct` | numeric | 100% | 180 | min 0 · median 2.5 · max 53 |
| 30 | `fp_cm_w15_49_condom_pct` | numeric | 100% | 244 | min 0 · median 6.1 · max 43.9 |
| 31 | `fp_cm_w15_49_injectables_pct` | numeric | 100% | 45 | min 0 · median 0.3 · max 9.8 |
| 32 | `fp_unmet_total_cm_w15_49_7_pct` | numeric | 100% | 187 | min 1.2 · median 8.5 · max 33 |
| 33 | `fp_unmet_spacing_cm_w15_49_7_pct` | numeric | 100% | 110 | min 0.3 · median 3.7 · max 25.2 |
| 34 | `health_worker_ever_talked_to_female_non_users_about_family_pct` | numeric | 100% | 326 | min 2 · median 23.1 · max 64.2 |
| 35 | `current_users_ever_told_about_side_effects_of_current_metho_pct` | numeric | 100% | 451 | min 14.6 · median 66.05 · max 98.9 |
| 36 | `mothers_who_had_an_anc_visit_in_the_first_trimester_lb5y_pct` | numeric | 100% | 383 | min 26.3 · median 73.75 · max 99.6 |
| 37 | `mothers_who_had_at_least_4_anc_visits_lb5y_pct` | numeric | 100% | 453 | min 4.4 · median 62.4 · max 98.7 |
| 38 | `mothers_whose_last_birth_was_protected_against_neo_tetanus_pct` | numeric | 100% | 203 | min 55.1 · median 92.7 · max 100 |
| 39 | `mothers_who_consumed_ifa_for_100_days_or_more_when_they_wer_pct` | numeric | 100% | 463 | min 1.6 · median 47.8 · max 95 |
| 40 | `mothers_who_consumed_ifa_for_180_days_or_more_when_they_wer_pct` | numeric | 100% | 423 | min 0.8 · median 24.55 · max 84.6 |
| 41 | `registered_pregnancies_for_which_the_mother_received_a_mcp_pct` | numeric | 100% | 137 | min 50 · median 97.6 · max 100 |
| 42 | `mothers_who_received_pnc_from_a_doctor_nurse_lhv_anm_midwif_pct` | numeric | 100% | 363 | min 24.9 · median 83.15 · max 99.5 |
| 43 | `average_out_of_pocket_expenditure_per_delivery_in_a_public_fac` | numeric | 100% | 666 | min 193 · median 2830 · max 2.01e+04 |
| 44 | `children_born_at_home_who_were_taken_to_a_health_facility_f_pct` | id/high-card | 40% | 132 | e.g. (0.0); 0.8 ; 0.0  … |
| 45 | `children_who_received_pnc_from_a_doctor_nurse_lhv_anm_midwi_pct` | numeric | 100% | 368 | min 22.4 · median 83.3 · max 99.6 |
| 46 | `institutional_birth_5y_pct` | numeric | 100% | 258 | min 21.4 · median 92.2 · max 100 |
| 47 | `institutional_birth_in_public_facility_5y_pct` | numeric | 100% | 423 | min 18.1 · median 66.5 · max 96.7 |
| 48 | `home_birth_that_were_conducted_by_skilled_hp_5y_10_pct` | numeric | 100% | 111 | min 0 · median 2.1 · max 19.9 |
| 49 | `births_attended_by_skilled_hp_5y_10_pct` | numeric | 100% | 255 | min 30.9 · median 92.3 · max 100 |
| 50 | `births_delivered_by_csection_5y_pct` | numeric | 100% | 375 | min 1.4 · median 18.6 · max 82.4 |
| 51 | `births_in_a_private_fac_that_were_delivered_by_csection_5y_pct` | id/high-card | 79% | 431 | e.g. (79.1); 73.8 ; 70.3  … |
| 52 | `births_in_a_public_fac_that_were_delivered_by_csection_5y_pct` | numeric | 100% | 344 | min 0.7 · median 12.95 · max 73 |
| 53 | `child_12_23m_fully_vaccinated_based_on_information_from_eit_pct` | numeric | 98% | 461 | min 38.3 · median 78 · max 100 |
| 54 | `child_12_23m_fully_vaccinated_based_on_information_from_vax_pct` | numeric | 97% | 408 | min 45 · median 84.95 · max 100 |
| 55 | `child_12_23m_who_have_received_bcg_pct` | numeric | 98% | 220 | min 65.9 · median 96 · max 100 |
| 56 | `child_12_23m_who_have_received_3_doses_of_polio_vaccine_pct` | numeric | 98% | 419 | min 47.6 · median 82.2 · max 100 |
| 57 | `child_12_23m_who_have_received_3_doses_of_penta_or_dpt_vacc_pct` | numeric | 98% | 373 | min 53.3 · median 88.8 · max 100 |
| 58 | `child_12_23m_who_have_received_the_first_dose_of_mcv_mcv_pct` | numeric | 98% | 348 | min 53.2 · median 89.6 · max 100 |
| 59 | `child_24_35m_who_have_received_a_second_dose_of_mcv_mcv_pct` | numeric | 98% | 457 | min 2.8 · median 31.4 · max 63.8 |
| 60 | `child_12_23m_who_have_received_3_doses_of_rotavirus_vaccine_pct` | numeric | 98% | 510 | min 0 · median 39.9 · max 100 |
| 61 | `child_12_23m_who_have_received_3_doses_of_penta_or_hepatiti_pct` | numeric | 98% | 414 | min 39.5 · median 86.3 · max 100 |
| 62 | `child_9_35m_who_received_a_vit_a_in_the_last_6_months_pct` | numeric | 100% | 385 | min 27.5 · median 73 · max 98.1 |
| 63 | `child_12_23m_who_received_most_of_their_vaccinations_in_a_p_pct` | numeric | 98% | 212 | min 67.1 · median 97.3 · max 100 |
| 64 | `child_12_23m_who_received_most_of_their_vaccinations_in_a_2_pct` | numeric | 98% | 174 | min 0 · median 1.6 · max 32.9 |
| 65 | `prev_diarrhoea_2wk_child_u5_pct` | numeric | 100% | 157 | min 0 · median 5.5 · max 39.3 |
| 66 | `children_with_diarrhoea_2wk_who_received_oral_rehydration_s_pct` | id/high-card | 30% | 196 | e.g. (72.9); (73.3); (74.4) … |
| 67 | `children_with_diarrhoea_2wk_who_received_zinc_child_u5_pct` | id/high-card | 30% | 190 | e.g. (23.0); (59.1); (24.0) … |
| 68 | `children_with_diarrhoea_2wk_taken_to_a_health_facility_or_h_pct` | id/high-card | 30% | 187 | e.g. (69.4); (51.5); (49.5) … |
| 69 | `children_prev_symptoms_of_acute_respiratory_infection_ari_2_pct` | numeric | 100% | 86 | min 0 · median 2.1 · max 11.2 |
| 70 | `children_with_fever_or_symptoms_of_ari_2wk_taken_to_a_healt_pct` | id/high-card | 68% | 382 | e.g. (85.7); (77.3); (79.7) … |
| 71 | `children_under_age_3_years_breastfed_within_one_hour_of_bir_pct` | numeric | 100% | 415 | min 7.8 · median 45.15 · max 88.5 |
| 72 | `child_u6m_exclusively_breastfed_pct` | id/high-card | 63% | 334 | e.g. (54.7); (77.4); (78.1) … |
| 73 | `child_6_8m_receiving_solid_or_semi_solid_food_and_breastmil_pct` | id/high-card | 9% | 61 | e.g. (35.4); (25.8); (69.4) … |
| 74 | `breastfeeding_child_6_23m_receiving_an_adequate_diet16_17_pct` | numeric | 99% | 336 | min 0 · median 10.2 · max 54.1 |
| 75 | `non_breastfeeding_child_6_23m_receiving_an_adequate_diet16_pct` | id/high-card | 9% | 56 | e.g. (10.7); (3.2); (6.8) … |
| 76 | `total_child_6_23m_receiving_an_adequate_diet16_17_pct` | numeric | 100% | 287 | min 0 · median 10.9 · max 50.1 |
| 77 | `child_u5_who_are_stunted_height_for_age_18_pct` | numeric | 100% | 304 | min 13.2 · median 32.85 · max 60.6 |
| 78 | `child_u5_who_are_wasted_weight_for_height_18_pct` | numeric | 100% | 240 | min 4.5 · median 18.1 · max 48 |
| 79 | `child_u5_who_are_severe_wasted_weight_for_height_19_pct` | numeric | 100% | 162 | min 0.5 · median 6.9 · max 30.5 |
| 80 | `child_u5_who_are_underweight_weight_for_age_18_pct` | numeric | 100% | 325 | min 7.2 · median 29.35 · max 62.4 |
| 81 | `child_u5_who_are_overweight_weight_for_height_20_pct` | numeric | 100% | 123 | min 0 · median 3.5 · max 21.1 |
| 82 | `women_age_15_49_years_whose_bmi_bmi_is_underweight_bmi_lt_1_pct` | numeric | 100% | 267 | min 1.2 · median 18 · max 43.6 |
| 83 | `women_age_15_49_years_who_are_overweight_obese_bmi_gte_25_0_pct` | numeric | 100% | 331 | min 3.8 · median 21.3 · max 53 |
| 84 | `women_age_15_49_years_who_have_high_risk_whr_gte_0_85_pct` | numeric | 100% | 379 | min 18 · median 58.15 · max 96.6 |
| 85 | `child_6_59m_who_are_anaemic_lt_11_0_g_dl_22_pct` | numeric | 100% | 347 | min 24.9 · median 67.7 · max 95.5 |
| 86 | `non_pregnant_w15_49_who_are_anaemic_lt_12_0_g_dl_22_pct` | numeric | 100% | 369 | min 15.6 · median 57.5 · max 94.6 |
| 87 | `pregnant_w15_49_who_are_anaemic_lt_11_0_g_dl_22_pct` | numeric | 81% | 430 | min 2 · median 51.9 · max 87.6 |
| 88 | `all_w15_49_who_are_anaemic_pct` | numeric | 100% | 359 | min 14.9 · median 57.2 · max 93.5 |
| 89 | `all_w15_19_who_are_anaemic_pct` | numeric | 100% | 372 | min 18.2 · median 59.75 · max 97.1 |
| 90 | `women_age_15_years_and_above_with_high_141_160_mg_dl_blood_pct` | numeric | 100% | 87 | min 1.6 · median 5.65 · max 14.6 |
| 91 | `w15_plus_with_very_high_gt_160_mg_dl_blood_sugar_pct` | numeric | 100% | 122 | min 0.7 · median 4.9 · max 18 |
| 92 | `w15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct` | numeric | 100% | 184 | min 4.1 · median 11.7 · max 32.1 |
| 93 | `m15_plus_with_high_141_160_mg_dl_blood_sugar_pct` | numeric | 100% | 99 | min 1.7 · median 6.8 · max 18.3 |
| 94 | `men_age_15_years_and_above_with_very_high_gt_160_mg_dl_bloo_pct` | numeric | 100% | 137 | min 0.5 · median 6.3 · max 21.1 |
| 95 | `m15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct` | numeric | 100% | 198 | min 4.8 · median 14.1 · max 36.2 |
| 96 | `w15_plus_with_mildly_high_bp_sys_140_159_mmhg_and_or_dia_90_pct` | numeric | 100% | 148 | min 4.3 · median 12.6 · max 23.7 |
| 97 | `w15_plus_with_moderately_or_severely_high_bp_sys_gte_160_mm_pct` | numeric | 100% | 97 | min 0.7 · median 5.1 · max 15.8 |
| 98 | `w15_plus_with_high_bp_sys_gte_140_mmhg_and_or_dia_gte_90_mm_pct` | numeric | 100% | 205 | min 8.5 · median 21 · max 42.1 |
| 99 | `m15_plus_with_mildly_high_bp_sys_140_159_mmhg_and_or_dia_90_pct` | numeric | 100% | 183 | min 5.3 · median 16.3 · max 32.9 |
| 100 | `m15_plus_with_moderately_or_severely_high_bp_sys_gte_160_mm_pct` | numeric | 100% | 118 | min 0.8 · median 5.8 · max 19.5 |
| 101 | `m15_plus_with_high_bp_sys_gte_140_mmhg_and_or_dia_gte_90_mm_pct` | numeric | 100% | 248 | min 10 · median 24.4 · max 49.6 |
| 102 | `women_age_30_49_years_ever_undergone_a_cervical_screen_pct` | numeric | 100% | 89 | min 0 · median 0.6 · max 23.2 |
| 103 | `women_age_30_49_years_ever_undergone_a_breast_exam_pct` | numeric | 100% | 58 | min 0 · median 0.2 · max 14.6 |
| 104 | `women_age_30_49_years_ever_undergone_an_oral_cancer_exam_pct` | numeric | 100% | 53 | min 0 · median 0.3 · max 15.8 |
| 105 | `w15_plus_who_use_any_kind_of_tobacco_pct` | numeric | 100% | 263 | min 0.1 · median 7.7 · max 70.6 |
| 106 | `m15_plus_who_use_any_kind_of_tobacco_pct` | numeric | 100% | 387 | min 6.8 · median 42.5 · max 80.6 |
| 107 | `w15_plus_who_consume_alcohol_pct` | numeric | 100% | 136 | min 0 · median 0.5 · max 42.8 |
| 108 | `m15_plus_who_consume_alcohol_pct` | numeric | 100% | 360 | min 0.1 · median 20.15 · max 68.4 |
