import Main, Config, Template
import pandas as pd

class Single:
    def __init__(self, config = None):
        self.config = config if config else config_global
    def main(self):
        self.annuity = template_maker.make_template(template_class = self.config.template_class)
        self.annuity_yield = self.config.claim/self.annuity.output_df.expected_reserves.values[0]

class Multi:
    def __init__(self):
        self.config = config_global
        self.interests = 0.01, 0.02, 0.03, 0.04, 0.05
        self.template_classes = Main.AnnuityTemplate, Main.AnnuityIncrementTemplate
        self.output_list = []
    def _make_template(self):
        self.annuity = Single()
        self.annuity.main()
        self.row.append(self.annuity.annuity_yield)
    def _make_templates(self):
        for interest in self.interests:
            self.config.mean_interest = interest
            self.row = [interest]
            for template_class in self.template_classes:
                self.config.template_class = template_class
                self._make_template()
            self.output_list.append(self.row)
    def _make_dataframe(self):
        self.dataframe = pd.DataFrame(self.output_list, columns = ['interest', 'annuity flat', 'annuity increment']).set_index('interest')
    def main(self):
        self._make_templates()
        self._make_dataframe()

config_global = Config.Config(False)
config_global.set_dfs(random_condition = 'fixed')
config_global.set_annuity()
config_global.annuity_start_age = 65
template_maker = Template.TemplateMaker(config_global)
