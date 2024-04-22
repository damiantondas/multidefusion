# Instructions for downloading a trial repository for MultiDEFusion library

The following repository has been created as a trial dataset to the MultiDEFusion library.
The complete documentation of the MultiDEFusion repository can be found at:
**https://damiantondas.github.io/multidefusion/**

## Cloning the Repository

To download the trial MultiDEFusion repository, follow these steps:

1. Open a terminal or command prompt on your computer.
2. Use the git clone command to clone the repository to your device:
`git clone https://github.com/damiantondas/multidefusion_trial.git`

3. The repository will be downloaded to the current directory. You can now navigate to the repository directory using the `cd` command:
`cd multidefusion_trial`

4. To run the procedure of integration in the Python environment, the initial parameters are required to define by user. In following, you can find an example script to run fusion for `ALL` stations in `multidefusion_trial` folder using `forward-backward` method with `0.03` mm/day^2^ noise level: 

    ```
    from multidefusion import run_fusion

    integration = run_fusion(stations="ALL", path="/path/to/multidefusion_trial/", method="forward-backward", noise=0.03)
    ```
5. More examples and description of the results can be found in the library documentation https://damiantondas.github.io/multidefusion/
