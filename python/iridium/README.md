# Iridium study

### [Arnaud Muller](https://www.github.com/Nosudrum) 2022/2023


## Generate Iridium states files

- [`iridium_TLEs`](iridium_TLEs.py) Get the latest TLEs of the Iridium NEXT constellation from CelesTrak
- [`iridium_synchronisation.py`](iridium_synchronisation.py) Propagate all Iridium satellites to the latest epoch of the
  TLEs to sync the constellation
- [`iridium_propagation.py`](iridium_propagation.py) Perform the propagation of the entire constellation alongside
  TOLOSAT chunk by chunk and export the states to pickle
  files.

## Analyze Iridium states to find visibility windows

- [`iridium_doppler`](iridium_doppler.py) For each propagation chunk and for each satellite, compute the Doppler shift
  and rate and check when they are below the threshold while geometrical visibilty conditions are satisfied.
- [`iridium_analysis`](iridium_analysis.py) Use the results of the previous script to create plots.


## Final results

![Iridium visibility](results/IRIDIUM_visibility.png)
![Iridium windows](results/IRIDIUM_windows.png)

## Doppler shift & rate of example satellite

![Doppler shift](results/IRIDIUM_100_doppler_shift.png)
![Doppler rate](results/IRIDIUM_100_doppler_rate.png)