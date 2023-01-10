import pandas as pd, math, Config

'''Class Tree
Insurance: claims use deaths, premiums in all years
    InsuranceInterest: recalculate interest when calculating actual reserves
    InsuranceExpected: expected = template.expected * policies
        InsuranceDeduct: deduct when higher than expected * 1.5 from year 1 to 30
        InsuranceAdd: add when lower than expected * 0.8
    Endowment: 30 year policy, everyone dies at year 29
    Annuity: claims use policies, premiums in year 0 only, adjustable start age
        AnnuityDeduct: InsuranceDeduct, expected * 1.211 from year 1 to 20
    _Cut Years: use self.input_df2, 25 year policy, last year is claim only
        Investment: claim at end, no deaths
        Multiple: death claim is years * premium, survival claim in last year
            MultipleDeduct: InsuranceDeduct, expected * 1.2 from year 5 to 18
_Template: calculate expected reserves for others to use
    InsuranceTemplate: Insurance
        EndowmentTemplate: Endowment
    AnnuityTemplate: Annuity, don't round
    InvestmentTemplate: Investment, don't round
    MultipleTemplate: Multiple, don't round
'''
'''Function Tree
__init__
    _load_transform_df
    _check_assertions
process_df
    _make_start_values
    for each row in self.input_df
        _update_deaths (Except Investment)
            _make_random_variable
        _append_row_to_output
        _update_policies (Except Investment)
    _make_output_df
    _calculate_claims
    _calculate_interest
        _make_random_variable
calculate_actual_reserves
    _calculate_interest (Only InsuranceInterest)
    _calculate_claims (Only Multiple)
    _calculate_premiums
    _adjust_reserves
calculate_expected_reserves (Only Template)
    _calculate_expected_reserves_one_year
'''

# Insurance
class Insurance():
    # __init__
    def _load_transform_df(self):
        self.input_df = self.config.input_df1.copy()
    def _check_assertions(self):
        for global_variable in self.config.claim, self.config.premium, self.config.start_policies:
            assert global_variable > 0
        for global_variable in self.config.mean_interest, self.config.sd_interest:
            assert 0 < global_variable < 1
    def __init__(self, config: Config.Config):
        self.round = True
        self.config = config
        self._load_transform_df()
        self._check_assertions()
    # process_df
    def _make_start_values(self):
        self.policies = self.config.start_policies
        self.deaths = 0
        self.output_df = []
    def _make_random_variable(self, rand_input: float, mean: float, sd: float) -> float:
        if self.config.random_condition == 'fixed':
            return mean
        elif self.config.random_condition in {'random_saved', 'random_dynamic'}:
            return rand_input * sd + mean
        else:
            raise Exception
    def _update_deaths(self):
        if self.row.qx == 1:
            # Because normal distribution of 100% binomial is nan
            self.deaths = self.policies
        else:
            # mean and sd are binomial
            mean_deaths = self.row.qx * self.policies
            sd_deaths = math.sqrt(mean_deaths * (1 - self.row.qx))
            self.deaths = self._make_random_variable(self.row.rand_deaths, mean_deaths, sd_deaths)
        if self.round:
            self.deaths = round(self.deaths, 0)
    def _append_row_to_output(self):
        self.output_df.append({'policies': self.policies, 'deaths': self.deaths})
    def _update_policies(self):
        self.policies -= self.deaths
    def _make_output_df(self):
        self.output_df = pd.DataFrame(self.output_df)
    def _calculate_claims(self):
        self.output_df['claims'] = 0
        # Claims pay based on last year's deaths
        self.output_df.loc[1:, 'claims'] = list(self.output_df.deaths[:-1] * self.config.claim)
    def _calculate_interest(self):
        self.output_df['interest'] = self.input_df.rand_interest.map(lambda rand_interest: self._make_random_variable(rand_interest, self.config.mean_interest, self.config.sd_interest))
    def process_df(self):
        self._make_start_values()
        for row in self.input_df.itertuples():
            self.row = row
            self._update_deaths()
            self._append_row_to_output()
            # Policies must only be updated after everything depending on it updates
            self._update_policies()
        self._make_output_df()
        self._calculate_claims()
        self._calculate_interest()
    # calculate_actual_reserves
    def _calculate_premiums(self):
        assert self.config.premium > 0
        self.output_df['premiums'] = self.output_df.policies * self.config.premium
    def _adjust_reserves(self, row, temp_reserves: float) -> float:
        return temp_reserves
    def calculate_actual_reserves(self, template = None):
        self._calculate_premiums()
        reserves = [self.output_df.premiums.values[0]]
        for row in self.output_df[1:].itertuples():
            temp_reserves = reserves[-1] * (1+row.interest) + row.premiums - row.claims
            reserves.append(self._adjust_reserves(row, temp_reserves))
        self.output_df['actual_reserves'] = reserves
        self.final_reserves = reserves[-1]
class InsuranceInterest(Insurance):
    def calculate_actual_reserves(self, template = None):
        # Recalculate interest when mean and sd interest have changed
        self._calculate_interest()
        super().calculate_actual_reserves()
class InsuranceExpected(Insurance):
    def calculate_actual_reserves(self, template):
        self.output_df['expected_reserves'] = template.output_df.expected_reserves * self.output_df.policies
        super().calculate_actual_reserves()
class InsuranceDeduct(InsuranceExpected):
    def __init__(self, config):
        super().__init__(config)
        self.min_year = 1
        self.max_year = 30
        self.deduct_threshold = 1.5
    def _adjust_reserves(self, row, temp_reserves: float) -> float:
        if self.min_year <= row.Index <= self.max_year:
            threshold = row.expected_reserves * self.deduct_threshold
            if temp_reserves > threshold:
                temp_reserves = threshold
            elif row.expected_reserves < 0:
                temp_reserves = 0
        return temp_reserves
class InsuranceAdd(InsuranceExpected):
    def _adjust_reserves(self, row, temp_reserves: float) -> float:
        if temp_reserves < row.expected_reserves * 0.8:
            temp_reserves = min(temp_reserves + row.premiums * 0.3, row.expected_reserves * 0.8)
        return temp_reserves

# Endowment
class Endowment(Insurance):
    def _load_transform_df(self):
        self.years = 30
        self.input_df = self.config.input_df1.copy()
        self.input_df = self.input_df[:self.years+1].reset_index(drop = True)
        # Everyone still alive is paid at end of last year
        self.input_df.loc[self.years-1:, 'qx'] = 1

# Annuity
class Annuity(Insurance):
    def _load_transform_df(self):
        super()._load_transform_df()
        # Class uses variable start age 60 and 80
        start_row = self.config.annuity_start_age - 40
        # Bug fix PQ7.4, AQ 7.4: excel misses last row
        end_row = len(self.input_df) 
        self.input_df = self.input_df[start_row:end_row].reset_index(drop = True)
        # Makes sure last rows's death probabilities stay 1
        end_subtract_row = 108 - self.config.annuity_start_age
        # Class uses death probabilities * 0.9
        self.input_df.loc[:(end_subtract_row), 'qx'] = self.input_df.loc[:(end_subtract_row), 'qx'] * 0.9
    def _calculate_claims(self):
        # Claims are paid to alive, not dead
        self.output_df['claims'] = self.output_df.policies * self.config.claim
    def _calculate_premiums(self):
        # Annuities only have 1 premium at year 0
        self.output_df['premiums'] = 0
        self.output_df.loc[0, 'premiums'] = self.output_df.policies[0] * self.config.premium
class AnnuityDeduct(Annuity, InsuranceDeduct):
    def __init__(self, config):
        super().__init__(config)
        self.max_year = 20 # Bug fix AQ7.5: Insurance is 30, annuity is 20
        self.deduct_threshold = 1.211

# Cut Years
class _CutYears(Insurance):
    def __init__(self, config):
        self.years = 25
        super().__init__(config)
    def _load_transform_df(self):
        # Final exam uses different qx
        self.input_df = self.config.input_df2.copy()
        # Cut number of years
        self.input_df = self.input_df[:self.years+1].reset_index(drop = True)
    def _calculate_premiums(self):
        super()._calculate_premiums()
        # Last row is for claim after all premiums are paid
        self.output_df.loc[25, 'premiums'] = 0
class Investment(_CutYears):
    def _calculate_claims(self):
        self.output_df['claims'] = 0
        # Last row is for claim after all premiums are paid
        self.output_df.loc[self.years, 'claims'] = self.output_df.policies[self.years] * self.config.claim
    def process_df(self):
        self._make_start_values()
        for row in self.input_df.itertuples():
            # No deaths in this product
            self._append_row_to_output()
        self._make_output_df()
        self._calculate_claims()
        self._calculate_interest()
class Multiple(_CutYears):
    def _calculate_claims(self):
        self.output_df['claims'] = 0
        # Death claims = premiums paid
        self.output_df.loc[1:, 'claims'] = list(self.output_df.deaths[:-1] * self.input_df.year[1:].reset_index(drop=True) * self.config.premium)
        # Survival claim for people alive at the end
        self.output_df.loc[self.years, 'claims'] += self.output_df.policies[self.years] * self.config.claim
    def calculate_actual_reserves(self, template = None):
        # Bug fix FE14: claims must be recalculated because it depends on premium
        self._calculate_claims()
        super().calculate_actual_reserves(template)
class MultipleDeduct(Multiple, InsuranceDeduct):
    def __init__(self, config):
        super().__init__(config)
        self.min_year = 5
        self.max_year = 18
        self.deduct_threshold = 1.2

# Template
class _Template(Insurance):
    def _calculate_expected_reserves_one_year(self, year: int):
        start_policies = self.output_df.policies.values[year]
        # Use nan to avoid divide by 0 warning
        start_policies = float('nan') if start_policies == 0 else start_policies
        self.multiplier = (1+self.config.mean_interest) ** year / start_policies
    def calculate_expected_reserves(self):
        # Discount doesn't depend on start year, so only needs to be calculated once
        self.discount = self.output_df.index.map(lambda x: (1+self.config.mean_interest) ** -x)
        self.output_df['expected_reserves'] = self.output_df.index.map(self._calculate_expected_reserves_one_year)
class InsuranceTemplate(_Template):
    def _calculate_expected_reserves_one_year(self, year: int) -> float:
        super()._calculate_expected_reserves_one_year(year)
        future_premiums = (self.output_df.policies[year+1:] * self.discount[year+1:]).sum()
        # Claims are based on previous year's deaths
        future_claims = (self.output_df.deaths[year:-1] * self.discount[year+1:]).sum()
        expected_reserves = (future_claims * self.config.claim - future_premiums * self.config.premium) * self.multiplier
        return expected_reserves
class EndowmentTemplate(Endowment, InsuranceTemplate):
    pass
class AnnuityTemplate(Annuity, _Template):
    def __init__(self, config):
        super().__init__(config)
        self.round = False
    def _calculate_expected_reserves_one_year(self, year: int) -> float:
        super()._calculate_expected_reserves_one_year(year)
        # Claims are based on number alive
        future_claims = (self.output_df.policies[year+1:] * self.discount[year+1:]).sum()
        # Premium is excluded because annuities don't have premiums after year 0
        expected_reserves = future_claims * self.config.claim * self.multiplier
        return expected_reserves
class InvestmentTemplate(Investment, _Template):
    def __init__(self, config):
        super().__init__(config)
        self.round = False
    def _calculate_expected_reserves_one_year(self, year: int) -> float:
        super()._calculate_expected_reserves_one_year(year)
        # Bug Fix: Same As Multiple Template
        future_claims = self.output_df.policies[self.years] * self.discount[self.years] if year < self.years else 0
        future_premiums = (self.output_df.policies[year+1:self.years] * self.discount[year+1:self.years]).sum()
        expected_reserves = (future_claims * self.config.claim - future_premiums * self.config.premium) * self.multiplier
        return expected_reserves
class MultipleTemplate(Multiple, _Template):
    def __init__(self, config):
        super().__init__(config)
        self.round = False
    def _calculate_expected_reserves_one_year(self, year: int) -> float:
        super()._calculate_expected_reserves_one_year(year)
        # Bug Fix FE 15: disable survival claim for last row because expected reserves only includes year+1
        future_survive = self.output_df.policies[self.years] * self.discount[self.years] if year < self.years else 0
        future_claims = (self.output_df.deaths[year:-1] * self.discount[year+1:] * self.output_df.index[year+1:]).sum()
        future_premiums = (self.output_df.policies[year+1:self.years] * self.discount[year+1:self.years]).sum()
        # Death claims are multiplied by premium
        expected_reserves = (future_survive * self.config.claim + (future_claims - future_premiums) * self.config.premium) * self.multiplier
        return expected_reserves