"""Strata CLI — unified command group."""
from __future__ import annotations

import click

from strata.cli.mcp import mcp
from strata.cli.chart import chart
from strata.cli.auth import auth
from strata.cli.conductor import conductor
from strata.cli.bootstrap import bootstrap
from strata.cli.check import check
from strata.cli.outputs import outputs
from strata.cli.dashboard import dashboard
from strata.cli.query import query


@click.group()
@click.version_option(package_name="strata")
def strata_cli() -> None:
    """Strata BI Agentic Toolkit — govern, analyze, and visualize LookML repos."""


strata_cli.add_command(mcp)
strata_cli.add_command(chart)
strata_cli.add_command(auth)
strata_cli.add_command(conductor)
strata_cli.add_command(bootstrap)
strata_cli.add_command(check)
strata_cli.add_command(outputs)
strata_cli.add_command(dashboard)
strata_cli.add_command(query)
