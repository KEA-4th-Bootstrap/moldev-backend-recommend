import os

import click
import uvicorn

from core.config import config


@click.command()
def main():
    uvicorn.run(
        app="app.server:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True,
        workers=1,
    )


if __name__ == "__main__":
    main()
