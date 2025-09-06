import argparse
from typing import List
from .schema import CliConfig

class CliInitialization(argparse.Namespace):
    def __init__(self, cli_config: CliConfig, **kwargs):
        super().__init__(**kwargs)
        self.cli_config = cli_config

        self.description = self.cli_config.description
        

    def parse_args_cli(self):
        parser = argparse.ArgumentParser(
            description=self.description
        )
        args = self.setup_args(parser)
        return args.parse_args()

    @staticmethod
    def setup_args(parser):
        parser.add_argument(
            "--mock",
            "-m",
            action="store_true",
            help="Use mock data for testing purposes (default: False)"
        )
        parser.add_argument(
            "--platform",
            "-p",
            type=str,
            choices=["tiktok", "youtube", "facebook"],
            required=True,
            default="tiktok",
            help="Target platform to collect data from (required)"
        )
        parser.add_argument(
            "--host_id",
            "-hi",
            type=str,
            required=True,
            default="@bacgau1989",
            help="Unique identifier for the host user who organized the stream (e.g., user123) (required)"
        )
        parser.add_argument(
            "--number_of_comments",
            "-nc",
            type=int,
            default=10,
            help="Number of comments to collect (default: 10)"
        )
        parser.add_argument(
            "--client_name",
            "-cn",
            type=str,
            default="tiktok_client",
            help="Name of the client for the platform (e.g., tiktok_client, youtube_client, facebook_client) (default: tiktok_client)"
        )

        parser.add_argument(
            "--events",
            "-e",
            type=str,
            nargs="+",
            default=["comment"],
            help="List of events associated with the information to be collected (e.g., comment, like, share, gifted, ...)"
        )

        return parser