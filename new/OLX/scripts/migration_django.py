import os
import subprocess


def run_migrations():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)

    operating_system = os.name

    # Change directory to the parent directory
    os.chdir(parent_directory)

    # Activate the virtual environment based on the operating system
    if operating_system == "posix":  # Linux or Mac OS
        activate_script = os.path.join(parent_directory, "env", "bin", "activate")
        activate_command = f"source {activate_script}"
    elif operating_system == "nt":  # Windows
        activate_script = os.path.join(parent_directory, "env", "Scripts", "activate")
        activate_command = f"call {activate_script}"
    else:
        print("Unsupported operating system")
        return

    # Run migrations
    migrate_command = "python manage.py migrate"

    try:
        subprocess.run(
            f"{activate_command} && {migrate_command}", shell=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")


if __name__ == "__main__":
    run_migrations()
