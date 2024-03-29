# Introduction
- This repository contains my homeworks for the [ANUx: Introduction to Actuarial Science | edX](https://www.edx.org/learn/actuarial-science/australian-national-university-introduction-to-actuarial-science) course
- I used Python to do the homeworks because:
    - The course used 1 excel spreadsheet for each simulation
    - There were 13 simulations each with 3 or 4 variations
    - It got very difficult to keep track of changes in different files
- In contrast, Python can use parent classes to write shared logic only once

# How to install the repository
- Clone it to your computer
- Install python 3.9
- Type `pip install -r requirements.txt`

# How to run the repository
- Everything can be run from notebook.ipynb
    - Call Main.py with different settings
    - Call Tester.py with different settings
    - Call Tester.py to run all simulation tests
    - Call Tester_Template.py to run all template tests
    - Call Tester_Annuity.py to test annuities

# Module Structure
- Tester files run the insurance policies and make sure their values match those from the class
    - Tester.py: run simulations with insurance policies, and check if success rate matches answer
    - Tester_Template: test insurance templates
    - Tester_Annuity: test effect of interest rates on regular and increment annuities
    - Each use the following classes
        - Main.py: contains different insurance policies
        - Config.py: contains settings for the program, accessible by all modules
        - Template.py: builds template from class, used by Handler and Tester

# Tester.py

## Class Tree
- Tester: count % of simulations with end reserves > 0
    - Insurance: Config.set_insurance, Main.Insurance(Interest, Deduct, Add)
        - InsuranceYear20: % of simulations with year 20 reserves > 0, Main.InsuranceExpected
        - InsuranceYearCount: % of years with actual > expected, Main.InsuranceExpected
    - Endowment: Config.set_insurance, Main.Endowment
    - Annuity: Config.set_annuity, Main.Annuity(Deduct)
    - Investment: Config.set_investment, Main.Investment
    - Multiple: Config.set_multiple, Main.Multiple(Deduct)
- Each class calls monte_carlo() with different premiums for different questions

## Function Tree
- __init__
    - Config.set_something
- make_simulations # Calculate once for all simulations, to save time, because it doesn't depend on premiums
    - for i in tqdm.trange(self.config.total_simulations):
        - Main.__init__
        - Main.process_df
- monte_carlo
    - _set_simulation_variables # Reset positive count
        - Template.make_template # Need to rebuild template to use new premium
    - _run_simulations
        - for simulation in self.simulations:
            - Main.calculate_actual_reserves # Must be recalculated when premium changes
            - _calculate_positive # Reserves > 0
    - _check_simulation_results # Only assert for random saved, so random numbers don't change

# Tester_Template.py

## Class Tree
- Each child class defines config settings/template class for the type of insurance, and assertion data (defined by class)
    - Insurance
    - Annuity
    - Investment
    - Multiple

## Function Tree
- __init__
    - config.set_something
- main
    - _make_template
        - template_maker.make_template
    - for row_number, answer in assertion_data
        - _assert_value

# Tester_Annuity.py

## Function Tree
- _make_templates
    - for interest in interests:
        - for template_class in template_classes
            - make_template
                - Single.main
                    - template_maker.make_template
- make_dataframe

# Main.py

## Class Tree
- Insurance: claims use deaths, premiums in all years, round
    - InsuranceInterest: recalculate interest when calculating actual reserves
    - InsuranceExpected: expected = template.expected * policies
        - InsuranceDeduct: deduct when higher than expected * 1.5 from year 1 to 30
        - InsuranceAdd: add when lower than expected * 0.8
    - Endowment: 30 year policy, everyone dies at year 29
    - Annuity: claims use policies, premiums in year 0 only, adjustable start age
        - AnnuityDeduct: InsuranceDeduct, expected * 1.211 from year 1 to 20
        - AnnuityIncrement: claim amount increases every year
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
    - _make_start_values # policies, deaths, dataframe
    - for each row in self.input_df
        - _update_deaths # Except Investment
            - _make_random_variable
        - _append_row_to_output
        - _update_policies # Except Investment
    - _make_output_df
    - _calculate_claims
    - _calculate_interest
        - _make_random_variable
- calculate_actual_reserves
    - _calculate_interest # Only InsuranceInterest
    - _calculate_claims # Only Multiple
    - _calculate_premiums # Often changes, so calculated with reserves
    - _adjust_reserves # Only Deduct and Add
- calculate_expected_reserves # Only Template
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
    - _read_random # Random numbers for simulations
        - _read_df
        - _norm_ppf
    - _read_input # Input also has random numbers, but can be replaced by random numbers
        - _read_df
        - _norm_ppf
- set_insurance
- set_annuity
- set_investment
- set_multiple