import config
import dash_html_components as html
import report
import views
import securities
import glob
import logging
from pathlib import Path

def base_path(parsed):
    return parsed.path.split('/')[2]


def find_root_configs(dir):
    files = glob.glob(str(dir / '*.yaml'))
    roots = set(files)
    for f in files:
        yaml = config.load_yaml(f)
        roots -= set([str(Path(dir) / name) for name in config.includes(yaml)])
    return tuple(roots)


class UIController:
    def __init__(self, path):
        path = Path(path if path else Path.cwd())
        if path.suffix == '.yaml':
            yamlpath = path
        else:
            roots = find_root_configs(path)
            yamlpath = roots[0]
        self.load_user_config(yamlpath)
        self.view = views.View()

    def load_user_config(self, path):
        self.cfg = config.UserConfig(path)
        logging.info(f'Loaded: {path}')

    def navbar(self):
        return self.view.navbar(self.cfg.account_names(), self.cfg.portfolio_names())

    def account_page(self, parsed):
        name = base_path(parsed)
        account = self.cfg.get_account(name)
        basic_df = report.account_basic_df(self.cfg, account)
        securities_df = report.account_securities_df(self.cfg, account)
        categories_df = report.account_categories_df(securities_df)
        hierarchy_df = report.account_hierarchy(securities_df)
        return self.view.account_page(name, basic_df, securities_df, categories_df, hierarchy_df)

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
        hierarchy_df = report.portfolio_hierarchy(portfolio_df)

        return self.view.portfolio_page(name, portfolio_df, compare_df, hierarchy_df)