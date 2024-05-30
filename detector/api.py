import re

import cloudscraper
from rich.table import Table
from rich.traceback import install as traceback_install
from user_agent import generate_user_agent

from .errors import InvalidChartData, InvalidServiceName
from .rconsole import console

traceback_install(theme="fruity")


class DownDetector:
    BASE_URL = "https://downdetector.com/status"
    COMPANY_PATTERN = re.compile(r"company: '(.*?)'")
    STATUS_PATTERN = re.compile(r"title'>\s*(.*?)\s*<")
    PERCENTAGE_PATTERN = re.compile(r"Chart_percentage'>\s*(\d+)%\s*<")
    NAME_PATTERN = re.compile(r"Chart_name'>\s*(.*?)\s*<")

    def __init__(self, service_name):
        self.service_name = service_name
        self.scraper = cloudscraper.create_scraper()

    def _fetch_data(self):
        response = self.scraper.get(
            f"{self.BASE_URL}/{self.service_name}/",
            headers={"User-Agent": generate_user_agent()},
        )
        return response.text

    def _parse_data(self, html):
        company = self.COMPANY_PATTERN.search(html)
        status = self.STATUS_PATTERN.search(html)
        if not (company and status):
            raise InvalidServiceName(
                f"Could not find the service name '{self.service_name}'"
            )
        return company.group(1), status.group(1)

    def _parse_chart_data(self, html):
        percentages = self.PERCENTAGE_PATTERN.findall(html)
        names = self.NAME_PATTERN.findall(html)
        if not (percentages and names):
            raise InvalidChartData(
                f"Could not find chart data for the service name '{self.service_name}'"
            )
        return [
            {"percentage": int(p), "name": n.strip()}
            for p, n in zip(percentages, names)
        ]

    def _display_status(self, company, status, chart_data):
        table = Table(
            title="(downdetector.com)",
            title_style="dodger_blue2",
            header_style="yellow",
        )
        table.add_column("Company", style="blue1", justify="center")
        table.add_column("Status", style="blue_violet", justify="center")
        table.add_column("Most Reported Problems", justify="center")

        problems = [
            f"[blue]{data['name']}[/] ([pale_green3]{data['percentage']}%[/])"
            for data in chart_data
        ]
        problems_str = "\n".join(problems)

        table.add_row(company, status, problems_str)
        console.print(table)

    def get_status(self):
        console.clear()
        html = self._fetch_data()
        company, status = self._parse_data(html)
        chart_data = self._parse_chart_data(html)
        self._display_status(company, status, chart_data)
