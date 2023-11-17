import Main, Config

def make_template(template_class) -> Main._Template:
    # 98620 is number alive at age 40 (Insurance Template uses rounding)
    config.random_condition, config.start_policies = 'fixed', 98620
    template = template_class(config = config)
    template.process_df()
    template.calculate_expected_reserves()
    config.random_condition, config.start_policies = random_condition, start_policies
    return template
