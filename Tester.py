import tqdm, Main, Config, typing

'''Class Tree
Tester: % of simulations with end reserves > 0
    Insurance
        InsuranceYear20: % of simulationss with year 20 reserves > 0
        InsuranceYearCount: % of years with actual > expected
    Endowment
    Annuity
    Investment
    Multiple
'''
'''Function Tree
__init__
    Config.set_global_variables
make_simulations
    Main.__init__
    Main.process_df
monte_carlo
    _set_simulation_variables
        Handler.make_template
    _run_simulations
        Main.calculate_actual_reserves
        _calculate_positive
    _check_simulation_results
'''

class Tester():
    def __init__(self, config: Config.Config, make_template: typing.Callable):
        self.config = config
        self.make_template = make_template
        self.template_class = None
    def make_simulations(self, insurance_class):
        self.simulations = []
        for i in tqdm.trange(self.config.total_simulations):
            simulation = insurance_class(config = self.config)
            simulation.input_df.rand_deaths = self.config.rand_deaths[i]
            simulation.input_df.rand_interest = self.config.rand_int[i]
            simulation.process_df()
            self.simulations.append(simulation)
    def _set_simulation_variables(self):
        # Bug fix PQ7.3: make sure template uses updated premium
        self.template = None if self.template_class is None else self.make_template(template_class = self.template_class)
        self.positive_count = 0
    def _calculate_positive(self, simulation: Main.Insurance) -> float:
        return float(simulation.final_reserves >= 0)
    def _run_simulations(self):
        for simulation in self.simulations:
            simulation.calculate_actual_reserves(template = self.template)
            self.positive_count += self._calculate_positive(simulation = simulation)
    def _check_simulation_results(self, answer: float):
        positive_ratio = self.positive_count/self.config.total_simulations
        positive_ratio = round(positive_ratio, 3)
        print(positive_ratio, answer)
        if self.config.random_condition == 'random_saved' and answer is not None:
            assert positive_ratio == answer, positive_ratio
    def monte_carlo(self, premium: float, answer: float):
        self.config.premium = premium
        self._set_simulation_variables()
        self._run_simulations()
        self._check_simulation_results(answer = answer)
class Insurance(Tester):
    def __init__(self, config, make_template):
        super().__init__(config, make_template)
        self.config.set_insurance()
        # Needed for pq73, aq73, pq72, aq72
        self.template_class = Main.InsuranceTemplate
    def aq66_pq63(self):
        self.make_simulations(insurance_class = Main.Insurance)
        self.monte_carlo(premium = 2265.98, answer = 0.42)
        self.monte_carlo(premium = 2000, answer = 0.195)
        self.monte_carlo(premium = 2500, answer = 0.61)
        self.monte_carlo(premium = 3285, answer = 0.9) # pq 6.3
    def aq67(self):
        self.make_simulations(insurance_class = Main.InsuranceInterest)
        self.config.mean_interest = 0.031
        self.config.sd_interest = 2.5 * 0.001
        self.monte_carlo(premium = 4375, answer = 0.9)
        self.config.mean_interest = 0.07
        self.config.sd_interest = 2.5 * 0.04
        self.monte_carlo(premium = 3050, answer = 0.9)
        self.config.mean_interest = 0.17
        self.config.sd_interest = 2.5 * 0.14
        self.monte_carlo(premium = 3975, answer = 0.9)
        self.config.set_insurance() # Reset mean_interest, sd_interest
    def pq73(self):
        self.make_simulations(insurance_class = Main.InsuranceDeduct)
        self.monte_carlo(premium = 2265.98, answer = 0.41)
        self.monte_carlo(premium = 2000, answer = 0.19)
        self.monte_carlo(premium = 2500, answer = 0.435)
    def aq73(self):
        self.make_simulations(insurance_class = Main.InsuranceAdd)
        self.monte_carlo(premium = 2265.98, answer = 0.455)
        self.monte_carlo(premium = 2000, answer = 0.36)
        self.monte_carlo(premium = 2500, answer = 0.615)
class InsuranceYear20(Insurance):
    def _calculate_positive(self, simulation: Main.Insurance) -> float:
        actual_higher_than_expected = simulation.output_df.actual_reserves[20] > simulation.output_df.expected_reserves[20]
        return float(actual_higher_than_expected)
    def pq72(self):
        self.make_simulations(insurance_class = Main.InsuranceExpected)
        self.monte_carlo(premium = 2265.98, answer = 0.39)
class InsuranceYearCount(Insurance):
    def _calculate_positive(self, simulation: Main.Insurance) -> float:
        actual_higher_than_expected = simulation.output_df.actual_reserves[1:-1] > simulation.output_df.expected_reserves[1:-1]
        return actual_higher_than_expected.mean()
    def aq72(self):
        self.make_simulations(insurance_class = Main.InsuranceExpected)
        self.monte_carlo(premium = 2265.98, answer = 0.438)
class Endowment(Tester):
    def __init__(self, config, make_template):
        super().__init__(config, make_template)
        self.config.set_insurance()
    def aq68(self):
        self.make_simulations(insurance_class = Main.Endowment)
        self.monte_carlo(premium = 7725, answer = 0.9)
class Annuity(Tester):
    def __init__(self, config, make_template):
        super().__init__(config, make_template)
        self.config.set_annuity()
        # Needed for aq75
        self.template_class = Main.AnnuityTemplate
    def pq74_aq75(self):
        self.config.annuity_start_age = 60
        self.make_simulations(insurance_class = Main.Annuity)
        premium = 390889.81
        self.monte_carlo(premium = premium * 1.0, answer = 0.47)
        self.monte_carlo(premium = premium * 0.9, answer = 0.07)
        self.monte_carlo(premium = premium * 1.1, answer = 0.87)
        self.monte_carlo(premium = 450000, answer = 0.975) # aq7.5
    def aq74(self):
        self.config.annuity_start_age = 80
        self.make_simulations(insurance_class = Main.Annuity)
        premium = 196939.02
        self.monte_carlo(premium = premium * 1.0, answer = 0.52)
        self.monte_carlo(premium = premium * 0.9, answer = 0.035)
        self.monte_carlo(premium = premium * 1.1, answer = 0.955)
    def aq75(self):
        self.config.annuity_start_age = 60
        self.make_simulations(insurance_class = Main.AnnuityDeduct)
        self.monte_carlo(premium = 450000, answer = 0.95)
class Investment(Tester):
    def __init__(self, config, make_template):
        super().__init__(config, make_template)
        self.config.set_investment()
    def fe5(self):
        self.make_simulations(insurance_class = Main.Investment)
        self.monte_carlo(premium = 5000, answer = 0.13)
class Multiple(Tester):
    def __init__(self, config, make_template):
        super().__init__(config, make_template)
        self.config.set_multiple()
        # Needed for fe16
        self.template_class = Main.MultipleTemplate
    def fe12_fe14(self):
        self.make_simulations(insurance_class = Main.Multiple)
        self.monte_carlo(premium = 7500, answer = 0.67)
        self.monte_carlo(premium = 8900, answer = 0.95) # fe_14
    def fe16(self):
        self.make_simulations(insurance_class = Main.MultipleDeduct)
        self.monte_carlo(premium = 7500, answer = 0.55)