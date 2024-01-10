import pandas as pd, random, time
from scipy.stats import norm

class Config():
    def __init__(self, simulate):
        self.simulate = simulate
        # Must be between 40 and 110
        self.annuity_start_age = 60
        self.set_insurance()
    def _read_df(self, sheet_name: str) -> pd.DataFrame:
        print(sheet_name)
        return pd.read_excel('Lesson_6_7_Python.xlsx', sheet_name=sheet_name)
    def _norm_ppf(self, rand_input: float) -> float:
        if self.random_condition == 'random_saved':
            return norm.ppf(rand_input)
        elif self.random_condition == 'random_dynamic':
            return norm.ppf(random.random())
        elif self.random_condition == 'fixed':
            return 0.5
        else:
            raise Exception
    def _read_input(self, sheet_name: str) -> pd.DataFrame:
        df = self._read_df(sheet_name = sheet_name)
        for column in 'rand_interest', 'rand_deaths':
            assert df[column].min() >= 0
            assert df[column].max() <= 1
            df[column] = df[column].map(self._norm_ppf)
        return df
    def _read_random(self, sheet_name: str) -> pd.DataFrame:
        df = self._read_df(sheet_name = sheet_name).drop('Simulation / Year', axis = 1).T
        assert df.min().min() >= 0
        assert df.max().max() <= 1
        timey = time.time()
        normal_df = df.map(self._norm_ppf)
        print(time.time() - timey)
        return normal_df
    def set_dfs(self, random_condition: str):
        '''This value can be changed: 
        fixed (always use mean)
        random_saved (use random numbers from excel)
        random_dynamic (use random numbers from python)'''
        self.random_condition = random_condition
        if self.simulate:
            '''
            These contain random numbers for 200 simulations
            Which numbers will be used depends on self.random_condition
            See self.set_other(), self.norm_ppf()
            It can be disabled because running 200 simulations is very slow
            '''
            self.rand_deaths = self._read_random(sheet_name = 'Rand Deaths')
            self.rand_int = self._read_random(sheet_name = 'Rand Int')
            self.total_simulations = len(self.rand_deaths.columns)
        self.input_df1 = self._read_input(sheet_name = 'Sheet1')
        self.input_df2 = self._read_input(sheet_name = 'Sheet2')
    def set_insurance(self):
        self.claim = 400000
        self.premium = 2265.98
        self.mean_interest = 0.06
        self.sd_interest = 0.075
        self.start_policies = 10000
    def set_annuity(self):
        self.claim = 25000
        self.premium = 390889.81
        self.mean_interest = 0.04
        self.sd_interest = 0.03
        self.start_policies = 5000
    def set_investment(self):
        self.claim = 250000
        self.premium = 5000
        self.mean_interest = 0.04
        self.sd_interest = 0.05
        self.start_policies = 10000
    def set_multiple(self):
        self.claim = 300000
        self.premium = 7500
        self.mean_interest = 0.04
        self.sd_interest = 0.05
        self.start_policies = 10000