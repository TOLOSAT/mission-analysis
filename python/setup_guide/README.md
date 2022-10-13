# Mission Analysis in Python (Detailed setup guide)

## 1 - Setting up git

### 1.1 - Installing GitHub Desktop

If you are an **experienced** git user, you can skip this section and go to the next one.

To contribute work to the GitHub repository, we recommend using (GitHub Desktop)[https://desktop.github.com/].
It has an easy to use graphical interface that allows you to `clone`, `pull`, `commit`, and `push` to repositories.

Download the installer, follow the instructions, then open the application and log in with your GitHub account.

### 1.2 - Cloning the repository

In GitHub Desktop, select `File` --> `Clone repository...` and select the `TOLOSAT/mission-analysis` repository.
You can place it wherever you want on your machine.

Once the repository is cloned, you can proceed to step 2.

## 2 - Setting up the Python environment

### 2.1 - Install Anaconda or Miniforge

If you already have [Anaconda](https://www.anaconda.com/) installed, you can use it. Otherwise, we recommend
installing [Miniforge](https://github.com/conda-forge/miniforge).

### 2.2 - Create the environment

On Mac, you will use the `Terminal`. On Windows, you will use `Anaconda prompt` or `Miniforge prompt`.
Use the `cd [path_to_repository]` command to navigate to the `python` sub-folder of the `mission-analysis` repository.
Your active path should look something like this: `.../GitHub/mission-analysis/python`.

Then, run the following command to create the environment:

```
conda env create -f environment.yaml
```

If any conflict is detected, use `CTRL+C` to cancel the operation and seek help from the team.

Once the installation is completed, you can proceed to step 3.

## 3 - Setting up the IDE

### 3.1 - Install PyCharm

If you already have a Python IDE of preference, you can use it, but you will need to configure the Python interpreter
yourself.

We recommend using [PyCharm](https://www.jetbrains.com/pycharm/).
A professional license is provided for free to students by
applying [here](https://www.jetbrains.com/shop/eform/students).

Once installed, proceed to step 3.2.

### 3.2 - Setting up PyCharm

In PyCharm, select `File` --> `Open...` and select the `mission-analysis` folder.
This will open the full project.

In the bottom right corner, you should see a `Python interpreter` dropdown menu. Follow the next steps:

- Click on the dropdown menu and select `Add New Interpreter`
- Click `Add Local Interpreter...`
- In the left panel, select `Conda Environment`
- In the `Interpreter` dropdown menu, select `tolosat-tudatpy`
- Click `OK`

Then, *right-click* on the `python` folder and select `Mark Directory as` --> `Sources Root`.

## 4 - Running the example code

In PyCharm, open the `python\examples\perturbed_satellite_orbit.py` file and run it with *right-click*
--> `Run 'perturbed_satellite_orbit'`.

If everything is set up correctly, you should see the following output:

```
State vector contains: 
Vector entries, Vector contents
[0:6], translational state of body Delfi-C3
Dependent variables being saved, output vector contains: 
Vector entry, Vector contents
0, Total acceleration in inertial frame of Delfi-C3
3, Kepler elements of Delfi-C3 w.r.t. Earth
9, Spherical position angle latitude angle of Delfi-C3 w.r.t. Earth
10, Spherical position angle longitude angle of Delfi-C3 w.r.t. Earth
11, Single acceleration norm of type central gravity , acting on Delfi-C3, exerted by Sun
12, Single acceleration norm of type central gravity , acting on Delfi-C3, exerted by Moon
13, Single acceleration norm of type central gravity , acting on Delfi-C3, exerted by Mars
14, Single acceleration norm of type central gravity , acting on Delfi-C3, exerted by Venus
15, Single acceleration norm of type spherical harmonic gravity , acting on Delfi-C3, exerted by Earth
16, Single acceleration norm of type aerodynamic , acting on Delfi-C3, exerted by Earth
17, Single acceleration norm of type cannonball radiation pressure , acting on Delfi-C3, exerted by Sun

Process finished with exit code 0
```

A total of four plots should also be displayed.

## Bonus - Running scripts in the Python console

To run scripts in the Python console, which allows to keep interacting with them after they are run and to
see all the variables and their value, you can follow the next steps:

- In the dropdown menu at the top right of your screen, left of the green `Run` button, click `Edit Configurations...`
- In the `Execution` category, enable `Run in Python Console`
- Click `OK`

You can now run the script again with the green `Run` button in the right corner.
The script will now run in the Python console and you will see all the variables created along with their type and
value.