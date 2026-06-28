"""Opportunity Assistant vertical slice application."""

from cios.applications.opportunity_assistant.pipeline import run_pipeline
from cios.applications.opportunity_assistant.reporting import render_console_report

__all__ = ["run_pipeline", "render_console_report"]
