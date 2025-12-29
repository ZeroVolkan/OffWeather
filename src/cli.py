import cmd

from loguru import logger
from typing import cast
from types import UnionType

from src.core.api import BaseAPI, ConfigAPI
from src.setting import Setting
from src.errors import APIError, EndpointError, ConfigError, SettingError
from src.utils import unwrap_and_cast, unwrap_union_type, parser_arguments

import src.static as static


class DebugShell(cmd.Cmd):
    prompt = "(debug) "
    intro = "Debug Shell for managing weather APIs"

    def __init__(self):
        super().__init__()
        self.api: BaseAPI | None = None
        self.config: ConfigAPI | None = None
        self.selected: str | None = None

        self.setting: Setting = Setting("setting.toml")
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

        self.apis = static.apis()
        self.workflows = static.workflows()


    def do_run(self, args):
        """Run API"""
        if self.api:
            try:
                args, kwargs = parser_arguments(args.split())
                self.api.run(**kwargs)
            except Exception as e:
                logger.error(f"Error running API: {e}")
        else:
            logger.error(
                f"Don't have instance for API: {self.selected if self.selected else 'Don"t selected'}"
            )


    def do_api(self, args):
        """Manage api

        Usage: api [select|list] <api_name>
        - select <api_name> : Select an API
        - list : List available APIs
        - up: Instance Api create
        - down: Instance Api delete
        - show: Show selected API information
        - run: Run selected API
        """
        parts = args.split(maxsplit=2)

        command = parts[0] if parts else ""
        api_name = parts[1] if len(parts) > 1 else None

        match command:
            case "select":
                if api_name is None:
                    print("Please provide an API name.")
                    return
                if api_name not in self.apis.keys():
                    print(f"API '{api_name}' not found.")
                    return
                self.selected = api_name
                logger.info(f"Selected API: {api_name}")
            case "list":
                print("Available APIs:")
                for api_name, api_info in self.apis.items():
                    print(f"  {api_name} ({api_info['class']})")
            case "up":
                if self.config is None:
                    print("No configuration loaded.")
                    return
                if self.selected is None:
                    print("No API selected.")
                    return
                try:
                    self.api = self.apis[self.selected]["class"](self.config)
                    logger.info(f"Created instance for API: {self.selected}")
                except APIError as e:
                    logger.error(
                        f"Failed to create instance for API: {self.selected}': {e}"
                    )
                except AttributeError as e:
                    logger.error(f"Failed to find attribute: '{self.selected}': {e}")
            case "down":
                if self.api:
                    del self.api
                    self.api = None
                    logger.info(f"Deleted instance for API: {self.selected}")
                else:
                    logger.error(f"Don't have instance for API: {self.selected}")
            case "show":
                if self.selected is None:
                    print("No API selected.")
                    return
                if self.api:
                    print(f"API: {self.selected}")
                    print(f"Config: {self.config}")
                    print(f"Instance: {self.api}")
                else:
                    print(f"Don't have instance for API: {self.selected}")
            case _:
                print("Invalid command.")
                print(self.do_api.__doc__)
                return

    def do_config(self, args):
        """Manage configuration settings.

        Usage: config [save|load|show|set|reset] [path|param value]
        - save [path] : Save configuration to TOML file
        - fetch [path] : Fetch configuration from TOML file
        - set [param] <value> : Set a configuration parameter
        - create : Create a new configuration file
        - show : Show current configuration
        - clear : Clear configuration
        """
        if not self.selected:
            print("❌ No API selected, please select an API first, use command api")
            return

        api = self.apis.get(self.selected)

        if not api:
            print(f"❌ API '{self.selected}' not found")
            return

        SelectedConfig = api["config"]

        if not SelectedConfig:
            print(f"❌ Configuration not found for API '{self.selected}'")
            return

        parts = args.split()
        command = parts[0] if parts else None

        path = parts[1:] if len(parts) > 1 else None

        param = parts[1] if len(parts) > 1 else None
        values = parts[2:] if len(parts) > 2 else [None]

        if not command:
            print(self.do_config.__doc__)
            return

        match command:
            case "save":
                if not path:
                    print("❌ Please provide a path to save the configuration")
                    return
                try:
                    self.config = self.setting.save(SelectedConfig, path)
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} saved to {path}"
                    )
                except ConfigError as e:
                    print(f"❌ {e}")
            case "fetch":
                if not path:
                    print("❌ Please provide a path to fetch the configuration")
                    return
                try:
                    self.config = self.setting.fetch(SelectedConfig, path)
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} fetched from {path}"
                    )
                except ConfigError as e:
                    print(f"❌ {e}")
            case "set":
                if not param:
                    print("❌ Please provide a parameter")
                    return
                if not self.config:
                    print("X Please load or create a configuration")
                    return
                if not hasattr(self.config, param):
                    print(f"X Parameter {param} does not exist")
                    return

                annotation = cast(UnionType, self.config.__annotations__.get(param))

                try:
                    if len(values) == 1:
                        values = values[0]

                    annotation = unwrap_union_type(annotation)
                    values = unwrap_and_cast(annotation, values)

                    setattr(self.config, param, values)
                except (ValueError, TypeError) as e:
                    print(f"❌ {e}")

                if not values:
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} clear {param}"
                    )
                else:
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} set {param} to {values}"
                    )
            case "create":
                if self.config:
                    print("❌ Configuration already exists")
                    return
                self.config = SelectedConfig()
                logger.info(f"Configuration {SelectedConfig.__name__} created")
            case "show":
                if not self.config:
                    print("❌ First load configuration")
                    return
                print(self.config)
            case "clear":
                if not self.config:
                    print("❌ Configuration isn't loaded")
                    return
                self.config = None
                logger.info(f"Configuration {SelectedConfig.__name__} cleared")
            case _:
                print("Invalid command.")
                print(self.do_config.__doc__)
                return

    def do_status(self, args):
        """Show status app"""
        print(
            f"{self.selected if self.selected else 'No selected'}: {self.config if self.config else "Don't have config"}"
        )
        if self.api:
            endpoints = ", ".join(map(lambda i: i.name(), self.api.all())) # type: ignore
            print(f"    Endpoint: {endpoints if endpoints else 'Not Found'}")
            print(f"    State: {self.api.state}")
        print(f"All Apis: {', '.join(self.apis.keys())}")

    def do_exit(self, args):
        """Exit the debug shell."""
        logger.info("Debug shell stopped")
        return 1

    def do_workflow(self, argument):
        """
        Usage [name]
        - None: show all workflows
        - With name: run a workflow
        """
        try:
            if argument:
                workflow = self.workflows[argument]
                workflow["executable"](self)
                logger.info(f"Workflow {argument} started")
            else:
                for key, value in self.workflows.items():
                    print(f"{key}: {value['description']}")
        except FileNotFoundError as e:
            logger.error(f"Workflow file don't found")
        except Exception as e:
            logger.error(f"Error workflow: {e}")


debug_shell = DebugShell()

if __name__ == "__main__":
    debug_shell.cmdloop()
