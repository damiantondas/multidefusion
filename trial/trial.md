# Instructions for downloading a trial repository for the MultiDEFusion library

The following repository has been created as a trial dataset for the MultiDEFusion library.
The dataset can be downloaded from GitHub or Zenodo platform.

## Cloning the repository from GitHub

1. Open a terminal or command prompt.
2. Use the git clone command to clone the repository to your device:
`git clone https://github.com/damiantondas/multidefusion_trial.git`

3. The repository will be downloaded to the current directory. You can now navigate to the repository directory using the `cd` command:
`cd multidefusion_trial`

## Cloning the repository from Zenodo

1. Go to the Zenodo repository: <a href="https://doi.org/10.5281/zenodo.11064301"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.11064693.svg" alt="Zenodo"></a>

2. Download the **multidefusion_trial.zip** folder.

3. Unzip the folder.

## Running the integration procedure

1. To run the integration procedure in the Python environment, the initial parameters are required to be defined by the user. In the following, you can find an example script to run fusion for `ALL` stations in `multidefusion_trial` folder using `forward-backward` method with `0.03` mm/day<sup>2</sup> noise level: 

    ```
    from multidefusion import run_fusion

    integration = run_fusion(stations="ALL", path="/path/to/multidefusion_trial/", method="forward-backward", noise=0.03)
    ```

2. More examples can be found in the [Usage](../usage/) section.
