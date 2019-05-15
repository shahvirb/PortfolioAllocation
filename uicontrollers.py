import config
import dash_html_components as html
import report
import views
import securities


def base_path(parsed):
    return parsed.path.split('/')[2]


class UIController:
    def __init__(self, path):
        self.cfg = config.UserConfig(path)
        self.view = views.View()

    def navbar(self):
        return self.view.navbar(self.cfg.account_names(), self.cfg.portfolio_names())

    def account_page(self, parsed):
        name = base_path(parsed)
        account = self.cfg.get_account(name)
        basic_df = report.account_basic_df(self.cfg, account)
        securities_df = report.account_securities_df(self.cfg, account)
        categories_df = report.account_categories_df(securities_df)
        return self.view.account_page(name, basic_df, securities_df, categories_df)

    def pagemap(self):
        pagemap = {
            '/': self.render_home_page
        }
        for name in self.cfg.account_names():
            pagemap[views.TEMPL_ACCT_HREF.format(name)] = self.account_page
        for name in self.cfg.portfolio_names():
            pagemap[views.TEMPL_PORT_HREF.format(name)] = self.portfolio_page
        return pagemap

    def layout(self):
        return self.view.layout(self.navbar())

    def render_home_page(self, parsed):
        securities_df = securities.symbol_categories_df(self.cfg)
        return self.view.home_page(securities_df)

    def portfolio_page(self, parsed):
        name = base_path(parsed)
        port = self.cfg.get_portfolio(name)
        portfolio_df = report.portfolio_df(self.cfg, port)
        compare_df = report.portfolio_target_comparison(self.cfg, port)
        return self.view.portfolio_page(name, portfolio_df, compare_df)