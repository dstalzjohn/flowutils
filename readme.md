# flowutils

**flowutils** is a command-line utility for managing your project structure and improving navigation
within your folder hierarchy. It allows you to create and organize projects easily, create symbolic links, 
and jump to specific project folders efficiently.

## Installation

Ensure that you have Python 3.x and the `pip` package manager installed. 
Then, you can install `flowutils` using the following command:

```shell
pip install flowutils
```

If you want a standalone installation you can use [pipx](https://pypa.github.io/pipx/) with the following
command:

```shell
pipx install flowutils
```

## Usage

### Initialize Configuration

Before using `flowutils`, you need to initialize the configuration. 
Run the following command to set up the necessary configuration file:

```shell
flow init
```

Follow the prompts to set the project and link locations. 
You can choose the default values or customize them according to your preferences.

### Create Project Directories

You can use the `create_project_dirs` command to generate project directories based on the defined project 
names and subdirectories. The subdirectories are currently only editable in the config file. The default location
is `~/.flowutils/config.yaml` if not specified otherwise in the `init` function.

This ensures a consistent and organized project structure:

```shell
flow create_project_dirs
```

### Add a Project

To add a new project to the configuration and create its corresponding directories, use the `add_project` command:

```shell
flow add_project <project>
```

Replace `<project>` with the name of your project.

### Add a Link

To add a new symbolic link, use the `add_link` command:

```shell
flow add_link <target_directory> <name>
```

Replace `<target_directory>` with the target directory path (absolute or relative), and `<name>` with the name of the link.

### Create Symbolic Links

The `create_links` command allows you to create symbolic links to specific files or directories. 
This can be useful for quick access to frequently used resources:

```shell
flow create_links
```

### Jump to Project Folders

One of the advantages of maintaining a clean project structure with `flowutils` is the ability to 
quickly jump to project directories. Simply use the `cd` shell command, followed by the name of your project:

```shell
cd <project>
```

Replace `<project>` with the desired project name, and you will be redirected to its corresponding directory.

## Advantages of a Clean Project Structure

Maintaining a well-organized project structure provides several benefits:

- **Improved productivity:** With a clear hierarchy and standardized locations for projects and resources, you can quickly locate and access the files or directories you need.

- **Simplified navigation:** `flowutils` allows you to jump to specific project folders effortlessly, saving time and reducing manual navigation efforts.

- **Consistency and collaboration:** A consistent project structure enables easier collaboration with team members. Everyone can understand the organization and access resources efficiently.

- **Better project management:** With an organized structure, it becomes easier to manage and maintain projects over time. You can quickly add new projects, create links, or make updates without the hassle of manual directory management.

By leveraging `flowutils` and maintaining a clean project structure, you can significantly streamline your development workflow and boost productivity.

---

**Note:** If you are using a Mac and the `forklift3` app, you can take advantage 
of its Shortcut Commands. You can use `CMD + SHIFT + G` you can easily jump to a specific directory. And with the links
added by flowutils, you can jump to nested directories with ease.

---

We hope that `flowutils` enhances your project management and navigation. 
If you have any questions or encounter any issues, please don't hesitate to reach out.

Happy flowing!

