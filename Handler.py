import Main, Tester, Config, Template, os

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

def test_annuity_yield():
    config.set_annuity()
    config.annuity_start_age = 65
    middle_interest = 0.035
    for template in Main.AnnuityTemplate, Main.AnnuityIncrementTemplate:
        for interest in middle_interest - 0.01, middle_interest, middle_interest + 0.01:
            config.mean_interest = interest
            annuity = template_maker.make_template(template_class = template)
            annuity_yield = config.claim/annuity.output_df.expected_reserves.values[0]
            print(template, [round(value * 100, 2) for value in [interest, annuity_yield]])
def test_insurance_template():
    config.set_insurance()
    insurance = template_maker.make_template(template_class = Main.InsuranceTemplate)
    assert round(insurance.output_df.expected_reserves.values[0]) == 2266, round(insurance.output_df.expected_reserves.values[0])
    # PQ 7.1
    assert round(insurance.output_df.expected_reserves.values[20]) == 68675
    # AQ 7.1
    assert round(insurance.output_df.expected_reserves.values[30]) == 129322
def test_annuity_template():
    config.set_annuity()
    config.annuity_start_age = 60
    annuity = template_maker.make_template(template_class = Main.AnnuityTemplate)
    assert round(annuity.output_df.expected_reserves.values[0]) == 390890
def test_investment_template():
    config.set_investment()
    investment = template_maker.make_template(template_class = Main.MultipleTemplate)
    assert round(investment.output_df.expected_reserves.values[20]) == 64760
def test_multiple_template():
    config.set_multiple()
    multiple = template_maker.make_template(template_class = Main.MultipleTemplate)
    # fe15
    assert round(multiple.output_df.expected_reserves.values[20]) == 215469
def test_random_saved():
    config.set_insurance()
    insurance = Main.Insurance(config = config)
    insurance.process_df()
    insurance.calculate_actual_reserves()
    if config.random_condition == 'random_saved':
        assert round(insurance.final_reserves) == 434802897, insurance.final_reserves
# Simulations
def test_insurance():
    tester_insurance = Tester.Insurance(config)
    tester_insurance.aq66_pq63()
    tester_insurance.aq67()
    tester_insurance.pq73()
    tester_insurance.aq73()
def test_insurance_years():
    tester_insurance = Tester.InsuranceYear20(config)
    tester_insurance.pq72()
    tester_insurance = Tester.InsuranceYearCount(config)
    tester_insurance.aq72()
def test_endowment():
    tester_endowment = Tester.Endowment(config)
    tester_endowment.aq68()
def test_annuity():
    tester_annuity = Tester.Annuity(config)
    tester_annuity.pq74_aq75()
    tester_annuity.aq74()
    tester_annuity.aq75()
def test_investment():
    tester_investment = Tester.Investment(config)
    tester_investment.fe5()
def test_multiple():
    tester_multiple = Tester.Multiple(config)
    tester_multiple.fe12_fe14()
    tester_multiple.fe16()    
# Handler
def test_all():
    test_annuity_yield()
    test_insurance_template()
    test_investment_template()
    test_annuity_template()
    test_multiple_template()
    test_random_saved()
    if SIMULATE:
        test_insurance()
        test_insurance_years()
        test_endowment()
        test_annuity()
        test_investment()
        test_multiple()

os.chdir(os.path.dirname(__file__))
SIMULATE = True
config = Config.Config(SIMULATE)
config.set_dfs(random_condition = 'random_saved')
template_maker = Template.TemplateMaker(config)
if __name__=='__main__':
    pass
    test_all()