# Introduction
- This repository contains my homeworks for the [ANUx: Introduction to Actuarial Science | edX](https://www.edx.org/learn/actuarial-science/australian-national-university-introduction-to-actuarial-science) course
- I used Python to do the homeworks because:
    - The course used 1 excel spreadsheet for each simulation
    - There were 13 simulations each with 3 or 4 variations
    - It got very difficult to keep track of changes in different files
- In contrast, Python can use parent classes to write shared logic only once

# Module Structure
- Handler.py: calls all the functions in Tester.py
    - Tester.py: run simulations with insurance policies, and check if success rate matches answer
        - Main.py: contains different insurance policies
- Config.py: contains settings for the program, accessible by all modules

# Notebook
- I've created notebook.ipynb to make it more convenient to:
    - Call Main.py with different settings
    - Call Tester.py with different settings
    - Call Handler.py to run all tests

# Tester.py

## Class Tree
- Tester: count % of simulations with end reserves > 0
    - Insurance: Config.set_insurance, Main.Insurance(Intrest, Deduct, Add)
        - InsuranceYear20: % of simulations with year 20 reserves > 0, Main.InsuraceExpected
        - InsuranceYearCount: % of years with actual > expected, Main.InsuraceExpected
    - Endowment: Config.set_insurance, Main.Endowment
    - Annuity: Config.set_annuity, Main.Annuity(Deduct)
    - Investment: Config.set_investment, Main.Investment
    - Multiple: Config.set_multiple, Main.Multiple(Deduct)
    - Each class calls monte_carlo() with different premiums for different questions

## Function Tree
- __init__
    - Config.set_<something>
- make_simulations
    - Main.__init__
    - Main.process_df
- monte_carlo
    - _set_simulation_variables
        - Template.make_template
    - _run_simulations
        - Main.calculate_actual_reserves
        - _calculate_positive
    - _check_simulation_results

# Main.py

## Class Tree
- Insurance: claims use deaths, premiums in all years
    - InsuranceInterest: recalculate interest when calculating actual reserves
    - InsuranceExpected: expected = template.expected * policies
        - InsuranceDeduct: deduct when higher than expected * 1.5 from year 1 to 30
        - InsuranceAdd: add when lower than expected * 0.8
    - Endowment: 30 year policy, everyone dies at year 29
    - Annuity: claims use policies, premiums in year 0 only, adjustable start age
        - AnnuityDeduct: InsuranceDeduct, expected * 1.211 from year 1 to 20
    - _Cut Years: use self.input_df2, 25 year policy, last year is claim only
        - Investment: claim at end, no deaths
        - Multiple: death claim is years * premium, survival claim in last year
            - MultipleDeduct: InsuranceDeduct, expected * 1.2 from year 5 to 18
- _Template: calculate expected reserves for others to use, don't round
    - InsuranceTemplate: Insurance, round
    - EndowmentTemplate: Endowment, round
    - AnnuityTemplate: Annuity
    - AnnuityIncrementTemplate: AnnuityIncrement
    - InvestmentTemplate: Investment
    - MultipleTemplate: Multiple

## Function Tree
- __init__
    - _load_transform_df
    - _check_assertions
- process_df
    - _make_start_values
    - for each row in self.input_df
        - _update_deaths (Except Investment)
            - _make_random_variable
        - _append_row_to_output
        - _update_policies (Except Investment)
    - _make_output_df
    - _calculate_claims
    - _calculate_interest
        - _make_random_variable
- calculate_actual_reserves
    - _calculate_interest (Only InsuranceInterest)
    - _calculate_claims (Only Multiple)
    - _calculate_premiums
    - _adjust_reserves
- calculate_expected_reserves (Only Template)
    - _calculate_expected_reserves_one_year

# Config.py

## Explanation
- set_dfs creates input data for policy, random numbers for simulations
- Other set_something functions contain preset combinations of constants for different questions in the course
    - claim: amount claimed by each policyholder
    - premium: premium paid by each policyholder
    - mean_interest: interest rate is modelled as normal distribution with mean and sd
    - sd_interest
    - start_policies: number of policyholders at start of policy

## Function Tree
- __init__
- set_dfs
    - _read_random
        - _read_df
        - _norm_ppf
    - _read_input
        - _read_df
        - _norm_ppf
- set_insurance
- set_annuity
- set_investment
- set_multiple