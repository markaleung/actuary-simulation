import Main

class TemplateMaker:
    def __init__(self, config):
        self.config = config
    def make_template(self, template_class) -> Main._Template:
        self.random_condition, self.start_policies = self.config.random_condition, self.config.start_policies
        # 98620 is number alive at age 40 (Insurance Template uses rounding)
        self.config.random_condition, self.config.start_policies = 'fixed', 98620
        self.template = template_class(config = self.config)
        self.template.process_df()
        self.template.calculate_expected_reserves()
        self.config.random_condition, self.config.start_policies = self.random_condition, self.start_policies
        return self.template
