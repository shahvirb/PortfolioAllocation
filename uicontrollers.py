import config
import dash_html_components as html
import report
import views


class UIController:
    def __init__(self, path):
        self.cfg = config.UserConfig(path)
        self.view = views.View()

    def navbar(self):
        return self.view.navbar(self.cfg.account_names(), self.cfg.portfolio_names())

    def account_page(self, name):
        account = self.cfg.get_account(name)
        basic_df = report.account_basic_df(self.cfg, account)
        securities_df = report.account_securities_df(self.cfg, account)
        categories_df = report.account_categories_df(securities_df)
        return self.view.account_page(name, basic_df, securities_df, categories_df)

    def render_account_page(self, parsed):
        name = parsed.path.split('/')[2]
        return self.account_page(name)

    def pagemap(self):
        pagemap = {
            '/': self.render_home_page
        }
        for name in self.cfg.account_names():
            pagemap[views.TEMPL_ACCT_HREF.format(name)] = self.render_account_page
        for name in self.cfg.portfolio_names():
            pagemap[views.TEMPL_PORT_HREF.format(name)] = lambda x: html.P(name)
        return pagemap

    def layout(self):
        return self.view.layout(self.navbar())

    def render_home_page(self, parsed):
        return self.view.home_page()