import click
import rich_click as click

from prompster.cli.commands import generate, model

BANNER = """\

  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗████████╗███████╗██████╗ 
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝███████╗   ██║   █████╗  ██████╔╝
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""

@click.rich_config(
    help_config=click.RichHelpConfiguration(
        style_header_text="bold magenta",
        style_option="bold cyan",
        style_switch="bold green",
        style_metavar="dim",
        style_commands_table_show_lines=True,
        style_options_panel_border="magenta",
        style_commands_panel_border="cyan",
        use_rich_markup=True,
        use_markdown=True,
    )
)
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        click.echo(click.style(BANNER, fg="magenta", bold=True))
        click.echo(
            "  "
            + click.style("Describe a theme", fg="cyan", bold=True)
            + click.style(" → ", fg="white")
            + click.style("get a Hitster deck.", fg="green")
        )
        click.echo(
            "\n  Run "
            + click.style("'prompster --help'", fg="yellow")
            + " to see available commands.\n"
        )

cli.add_command(generate)
cli.add_command(model)