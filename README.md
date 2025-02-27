# Mission Analysis

You can find the complete mission analysis document on Valispace [here](https://tolosat.valispace.com/project/26/analyses/32).

## Mission statement
The Mission Analysis subsystem is dedicated to the following tasks :
- Select and define the orbit in which the spacecraft shall be injected at launch.
- Propagate the spacecraft trajectory, compute eclipses, communication windows and supply position & velocity data for other simulations.
- Analyse the evolution of the orbit in the short- and long-term to ensure compliance with regulations and mission requirements.
- Identify how the evolution of the orbit impacts mission operations and payloads performance.
- Provide other subsystems with support and training in orbital mechanics to help them ensure their subsystem is able to satisfy performance requirements in the short and long-term.

## Project Management
The dashboard of the Mission Analysis team can be found [here](https://github.com/orgs/TOLOSAT/projects/1/views/1).
Open issues are available [here](https://github.com/TOLOSAT/mission-analysis/issues).
Progress on the main milestones is visible [here](https://github.com/TOLOSAT/mission-analysis/milestones).

## Table of Contents
<!-- Start TOC (do not remove me) -->
* [Python](python)
  * [Input data](python/input_data)
  * [Iridium studies](python/iridium)
  * [Long-term eclipses study](python/long_term_eclipses)
  * [Setup guide](python/setup_guide)
  * [Useful functions](python/useful_functions)
* [CelestLab](celestlab) (⚠️ deprecated)
  * [Setup guide](celestlab/Celestlabsetup)
  * [Solar activity data](celestlab/Data)
  * [Export trajectory for other subsystems](celestlab/ExportTrajectory)
  * [Iridium studies](celestlab/Iridium)
  * [Impact of launch year on mission duration](celestlab/LaunchYearMissionDuration)
  * [Long-term eclipses](celestlab/LongTermEclipses)
  * [Impacts of orbit insertion errors](celestlab/OrbitInsertionErrors)
  * [Generate pretty visuals](celestlab/PrettyVisuals)
  * [Generate plots with python](celestlab/PythonPlots)
  * [SATNOGS studies](celestlab/SATNOGS)
* [Orekit](orekit) (⚠️ deprecated)
<!-- End TOC (do not remove me) -->

## How to use GitHub
If you are new to git and GitHub, we recommend using [GitHub Desktop](https://desktop.github.com/).

Once installed and logged in, `clone` this repository, then `fetch` and `pull` to download the repository on your machine.
When ready to upload your work, select which changes to include, fill in some basic description then `commit` & `push`.
