import argparse
import pathlib
import subprocess
import configparser


class Config:
    def __init__(self, priority, command=None, config_file=pathlib.Path("config.ini"), hypervisor=None,
                 output_path=pathlib.Path().cwd(), packer_path=pathlib.Path().cwd(), update_config=False):
        self.command = command
        self.config_file = config_file
        self.hypervisor = hypervisor
        self.output_path = output_path
        self.packer_path = packer_path
        self.update_config = update_config
        self.priority = priority


def parse_args():
    parser = argparse.ArgumentParser()

    # what subcommand to use
    subcommands = ["create", "destroy"]
    parser.add_argument("command", type=str, choices=subcommands, metavar="command",
                        help="Subcommand to run")

    # what hypervisor to use
    supported_hypervisors = ["virtualbox", "vmware-workstation-pro", "vmware-fusion"]
    parser.add_argument("-hy", "--hypervisor", type=str, choices=supported_hypervisors,
                        dest="hypervisor", help="Which hypervisor to create the VM with")

    # Packer Executable
    parser.add_argument("-p", "--packer-path", type=pathlib.Path, dest="packer_path",
                        help="Path to the packer binary")

    # Output folder for VM
    parser.add_argument("-o", "--output-path", type=pathlib.Path, dest="output_path",
                        help="Path to the output directory for the VM created")

    # Update the config file default values
    parser.add_argument("-u", "--update-config", action='store_true', dest="update_config",
                        help="Update the config file using the values passed in the command line where applicable")

    # Read from config file
    parser.add_argument("-f", "--config-file", type=pathlib.Path, dest="config_file",
                        help="Use defaults from a config file")

    args = parser.parse_args()

    return Config(0, args.command, args.config_file, args.hypervisor,
                  args.output_path, args.packer_path, args.update_config)


def find_packer_path():
    pass


def update_config_file(args):
    pass


def handle_args(args):
    # Handle Hypervisor
    if args.hypervisor is None:
        print("Please specify a hypervisor")
        exit(1)

    # Handle Packer Path
    if args.packer_path is None:
        packer_path = find_packer_path()
        if packer_path is None:
            print("Packer path not found")
            exit(1)
    else:
        if not pathlib.Path(args.packer_path).exists():
            print(f'Packer path does not exist: {args.packer_path}')
            exit(1)

        completed_command = subprocess.run("%s version" % args.packer_path, capture_output=True)
        if completed_command.returncode != 0 or "Packer" not in str(completed_command.stdout):
            print(f'Packer executable not present in path: {args.packer_path}')
            exit(1)

    # Handle Output Path
    if args.output_path is None:
        args.output_path = pathlib.Path().cwd()

    # Handle Update Config
    if args.update_config_file:
        update_config_file(args)

    # Handle Config File
    if args.config_file is None:
        default_config_name = "config.ini"
        if pathlib.Path(default_config_name).exists():
            args.config_file = pathlib.Path(default_config_name)
    else:
        if not pathlib.Path(args.config_file).exists():
            print(f'Config file does not exist: {args.config_file}')
            exit(1)


def get_config_parser_attribute(config_parser, attribute):
    parsed_attribute = None
    if config_parser.has_option("default", attribute):
        if len(config_parser.get("default", attribute)) > 0:
            parsed_attribute = config_parser.get("default", attribute)

    return parsed_attribute


def parse_config_file(config_file, priority):
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)

    hypervisor = get_config_parser_attribute(config_parser, "hypervisor")
    packer_path = get_config_parser_attribute(config_parser, "packer_path")
    output_path = get_config_parser_attribute(config_parser, "output_path")

    return Config(priority=priority, hypervisor=hypervisor, packer_path=packer_path,
                  output_path=output_path)


def rectify_configs(*configs):
    sorted_configs = sorted(configs, key=lambda config: config.priority, reverse=True)
    final_config = sorted_configs.pop(0)

    attributes_to_check = ["command", "config_file", "hypervisor", "output_path",
                           "packer_path", "update_config", "priority"]

    for config in sorted_configs:
        for attribute in attributes_to_check:
            if getattr(config, attribute) is not None:
                setattr(final_config, attribute, getattr(config, attribute))

    return final_config


def determine_config():
    # Determine command line options
    command_line_config = parse_args()

    # Determine default config file options
    default_config_file = pathlib.Path("config.ini")
    if default_config_file.exists():
        default_config = parse_config_file(default_config_file, priority=2)
        default_config.config_file = default_config_file

    # Determine custom config file options
    custom_config_file = command_line_config.config_file
    if custom_config_file is not None:
        custom_config = parse_config_file(command_line_config.config_file, priority=1)
        custom_config.config_file = custom_config_file

    return rectify_configs(command_line_config, default_config, custom_config)


def main():
    config = determine_config()
    print()


if __name__ == '__main__':
    main()
