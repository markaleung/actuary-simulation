import Template, Main, Config

class Tester:
    def __init__(self):
        self.config = config_global

class Insurance(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_insurance()
    def main(self):
        self.insurance = template_maker.make_template(template_class = Main.InsuranceTemplate)
        assert round(self.insurance.output_df.expected_reserves.values[0]) == 2266, round(self.insurance.output_df.expected_reserves.values[0])
        # PQ 7.1
        assert round(self.insurance.output_df.expected_reserves.values[20]) == 68675
        # AQ 7.1
        assert round(self.insurance.output_df.expected_reserves.values[30]) == 129322

class Annuity(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_annuity()
        self.config.annuity_start_age = 60
    def main(self):
        self.annuity = template_maker.make_template(template_class = Main.AnnuityTemplate)
        assert round(self.annuity.output_df.expected_reserves.values[0]) == 390890

class Investment(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_investment()
    def main(self):
        self.investment = template_maker.make_template(template_class = Main.InvestmentTemplate)
        assert round(self.investment.output_df.expected_reserves.values[0]) == 17544

class Multiple(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_multiple()
    def main(self):
        self.multiple = template_maker.make_template(template_class = Main.MultipleTemplate)
        # fe15
        assert round(self.multiple.output_df.expected_reserves.values[20]) == 215469

CLASSES = {name: eval(name) for name in ['Insurance', 'Annuity', 'Investment', 'Multiple']}
config_global = Config.Config(False)
config_global.set_dfs(random_condition = 'random_saved')
template_maker = Template.TemplateMaker(config_global)
