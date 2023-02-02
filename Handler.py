import Main, Tester, Config

'''Module Tree
Handler
    Config
    Tester
        Config
        Main
            Config
    Main
        Config
'''

def make_template(template_class) -> Main._Template:
    random_condition, start_policies = config.random_condition, config.start_policies
    # 98620 is number alive at age 40 (Insurance Template uses rounding)
    config.random_condition, config.start_policies = 'fixed', 98620
    template = template_class(config = config)
    template.process_df()
    template.calculate_expected_reserves()
    config.random_condition, config.start_policies = random_condition, start_policies
    return template
def test_fixed_template():
    config.set_insurance()
    insurance = make_template(template_class = Main.InsuranceTemplate)
    assert round(insurance.output_df.expected_reserves.values[0]) == 2266
    # PQ 7.1
    assert round(insurance.output_df.expected_reserves.values[20]) == 68675
    # AQ 7.1
    assert round(insurance.output_df.expected_reserves.values[30]) == 129322
    config.set_annuity()
    config.annuity_start_age = 60
    annuity = make_template(template_class = Main.AnnuityTemplate)
    assert round(annuity.output_df.expected_reserves.values[0]) == 390890
    config.set_multiple()
    multiple = make_template(template_class = Main.MultipleTemplate)
    # fe15
    assert round(multiple.output_df.expected_reserves.values[20]) == 215469
def test_random_saved():
    config.set_insurance()
    insurance = Main.Insurance(config = config)
    insurance.process_df()
    insurance.calculate_actual_reserves()
    if config.random_condition == 'random_saved':
        assert round(insurance.final_reserves) == 434802897, insurance.final_reserves
def test_insurance():
    tester_insurance = Tester.Insurance(config, make_template)
    tester_insurance.aq66_pq63()
    tester_insurance.aq67()
    tester_insurance.pq73()
    tester_insurance.aq73()
def test_insurance_years():
    tester_insurance = Tester.InsuranceYear20(config, make_template)
    tester_insurance.pq72()
    tester_insurance = Tester.InsuranceYearCount(config, make_template)
    tester_insurance.aq72()
def test_endowment():
    tester_endowment = Tester.Endowment(config, make_template)
    tester_endowment.aq68()
def test_annuity():
    tester_annuity = Tester.Annuity(config, make_template)
    tester_annuity.pq74_aq75()
    tester_annuity.aq74()
    tester_annuity.aq75()
def test_investment():
    tester_investment = Tester.Investment(config, make_template)
    tester_investment.fe5()
def test_multiple():
    tester_multiple = Tester.Multiple(config, make_template)
    tester_multiple.fe12_fe14()
    tester_multiple.fe16()    
def test_all():
    test_fixed_template()
    test_random_saved()
    test_insurance()
    test_insurance_years()
    test_endowment()
    test_annuity()
    test_investment()
    test_multiple()

config = Config.Config()
if __name__=='__main__':
    pass
    test_all()