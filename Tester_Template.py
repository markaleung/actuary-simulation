import Template, Main, Config

class Tester:
    def __init__(self):
        self.config = config_global
    def _make_template(self):
        self.template = template_maker.make_template(template_class = self.template_class)
    def _assert_value(self):
        self.expected_reserves = round(self.template.output_df.expected_reserves.values[self.row_number])
        assert self.expected_reserves == self.answer, [self.expected_reserves, self.answer]
    def main(self):
        self._make_template()
        for row_number, answer in self.assertion_data:
            self.row_number = row_number
            self.answer = answer
            self._assert_value()

class Insurance(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_insurance()
        self.template_class = Main.InsuranceTemplate
        self.assertion_data = [
            [0, 2266], 
            [20, 68675], # PQ 7.1
            [30, 129322], # AQ 7.1
        ]

class Annuity(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_annuity()
        self.config.annuity_start_age = 60
        self.template_class = Main.AnnuityTemplate
        self.assertion_data = [[0, 390890]]

class Investment(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_investment()
        self.template_class = Main.InvestmentTemplate
        self.assertions = [[0, 17544]]

class Multiple(Tester):
    def __init__(self):
        super().__init__()
        self.config.set_multiple()
        self.template_class = Main.MultipleTemplate
        self.assertion_data = [[20, 215469]] # fe15

CLASSES = {name: eval(name) for name in ['Insurance', 'Annuity', 'Investment', 'Multiple']}
config_global = Config.Config(False)
config_global.set_dfs(random_condition = 'random_saved')
template_maker = Template.TemplateMaker(config_global)
