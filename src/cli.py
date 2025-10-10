import cmd, sys

from loguru import logger
from typing import cast
from types import UnionType

from .core.api import WeatherAPI, ConfigAPI
from .setting import Setting
from .errors import ApiError, EndpointError, ConfigError, CommandError, SettingError
from .utils import unwrap_and_cast, unwrap_union_type, parser_arguments

import src.static as static

class DebugShell(cmd.Cmd):
    prompt = "(debug) "
    intro = "Debug Shell for managing weather APIs"

    def __init__(self):
        super().__init__()
        self.api: WeatherAPI | None = None
        self.config: ConfigAPI | None = None
        self.selected: str | None = None

        self.setting: Setting = Setting("setting.toml")
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

        self.apis = static.apis()
        self.workflows = static.workflows()


    def do_api(self, args):
        """Manage api

        Usage: api [select|list] <api_name>
        select <api_name> : Select an API
        list : List available APIs
        up: Instance Api create
        down: Instance Api delete
        show: Show selected API information
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
                except ApiError as e:
                    logger.error(
                        f"Failed to create instance for API: {self.selected}': {e}"
                    )
                except AttributeError as e:
                    logger.error(f"Failed to find API: '{self.selected}': {e}")
            case "down":
                if self.selected is None:
                    print("No API selected.")
                    return
                if self.api:
                    del self.api
                    self.api = None
                    logger.info(f"Deleted instance for API: {self.selected}")
            case "show":
                if self.selected is None:
                    print("No API selected.")
                    return
                if self.api:
                    print(f"API: {self.selected}")
                    print(f"Config: {self.config}")
                    print(f"Instance: {self.api}")
                else:
                    print(f"No instance for API: {self.selected}")
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
        """Show status cli"""
        print(f"{self.selected}: {self.api} - All: {', '.join(self.apis.keys())}")
        if self.api:
            print(f"    Avalible: {', '.join(self.api.commands.keys()) if self.api.commands else "Don't commands available"}")
            print(f"    Endpoint: {', '.join(self.api.endpoints.keys()) if self.api.endpoints else "Don't endpoints available"}")
        print(f"Config: {self.config if self.config else "Don't have config"}")


    def do_exit(self, args):
        """Exit the debug shell."""
        logger.info("Debug shell stopped")
        return 1

    def do_commands(self, args):
        """List information about available commands"""
        if not self.api:
            print("❌ First create API")
            return
        if self.api.commands:
            for name, command in self.api.commands.items():
                print(f"Command {name}: {command.__doc__}")
        else:
            print("❌ No commands available")
        return 0

    def do_unsafe(self, args):
        """Allow all available commands"""
        if not self.api:
            print("❌ First create API")
            return

        self.api.admin()
        logger.info("All commands available")

    def do_exec(self, args: str):
        """Run an available command

        - execute 'Command' arguments (positional) key=value (named)
        """
        if not self.api:
            print("❌ First create API")
            return

        parts = args.split()

        if len(parts) == 0:
            raise ValueError("No command provided")

        command = parts[0]
        argumets, kwargs = parser_arguments(parts[1:])

        try:
            logger.info(f"Executing command {command} with params {argumets, kwargs}")
            self.api.execute(command, *argumets, **kwargs)
        except CommandError as e:
            logger.error(f"Error executing command {command}: {e}")
        except SettingError as e:
            logger.error(f"Error setting command {command}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing command {command}: {e}")

    def do_workflow(self, argument):
        """Works with workflow

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

    # MODIFACATE
    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.
        """
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete) # type: ignore
                if readline.backend == "editline": # type: ignore
                    if self.completekey == 'tab':
                        command_string = "bind ^I rl_complete"
                    else:
                        command_string = f"bind {self.completekey} rl_complete"
                else:
                    command_string = f"{self.completekey}: complete"
                readline.parse_and_bind(command_string)
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                self.stdout.flush()  # CHANGE
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

debug_shell = DebugShell()

if __name__ == "__main__":
    debug_shell.cmdloop()
