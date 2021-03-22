import click
@app.cli.command()
@click.option('--drop', is_flag_True, help='Create after drop.')
def initdb(drop):
    """Initlialize the database"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')
