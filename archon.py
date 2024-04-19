import argparse
import pathlib
import subprocess


def parse_args():
    parser = argparse.ArgumentParser()

    # what subcommand to use
    subcommands = ["create", "destroy"]
    parser.add_argument("command", type=str, choices=subcommands, metavar="command",
                        help="Subcommand to run")

    # what hypervisor to use
    supported_hypervisors = ["vmware-workstation-pro"]
    parser.add_argument("-hy", "--hypervisor", type=str, choices=supported_hypervisors,
                        dest="hypervisor", help="Which hypervisor to create the VM with")

    # Packer Installation
    parser.add_argument("-p", "--packer-path", type=pathlib.Path, dest="packer_path",
                        help="Path to the packer binary")

    # Output folder for VM
    parser.add_argument("-o", "--output-path", type=pathlib.Path, dest="output_path",
                        help="Path to the output directory for the VM created")

    # Update the config file default values
    parser.add_argument("-u", "--update-config", action='store_true', dest="update_config",
                        help="Update the config file using the values passed in the command line where applicable")

    # Read from config file
    parser.add_argument("-f", "--file", type=pathlib.Path, dest="config_file",
                        help="Use defaults from a config file")

    return parser.parse_args()


def find_packer_path():
    pass


def update_config(args):
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
    if args.update_config:
        update_config(args)

    # Handle Config File
    if args.config_file is None:
        default_config_name = "config.toml"
        if pathlib.Path(default_config_name).exists():
            args.config_file = pathlib.Path(default_config_name)
    else:
        if not pathlib.Path(args.config_file).exists():
            print(f'Config file does not exist: {args.config_file}')
            exit(1)


def main():
    args = parse_args()
    handle_args(args)
    print()


if __name__ == '__main__':
    main()
