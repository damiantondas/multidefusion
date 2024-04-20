# Input files structure

A maintenance of the specific structure for all input files is necessary to ensure the successful accomplishment of the integration procedure.

## The input file names structure:

1. GNSS: "GNSS.txt" (Mandatory file)
2. InSAR: (e.g., "DInSAR_Asc_1.txt", "DInSAR_Asc_2.txt", "SBAS_51_main.txt", "PSI_123.txt", ...)
    - '*Type*'_'*Orbit*'.txt OR
    - '*Type*'\_'*Orbit*'_'*Element*'.txt. The '*Element*' part is not mandatory.
     where:
      - '*Type*' is a mandatory signature of InSAR calculation method. Allowed values: "DInSAR", "SBAS" or "PSI".
      - '*Orbit*' is a mandatory signature of InSAR orbit. Allowed types: `str` or `int`, e.g., "Asc", "Desc", "51", "123", ...
      - '*Element*' is a non-mandatory signature of particular pixel or PS point. Allowed types: `str` or `int`, e.g., "1", "10254", "main", ...
      
## Restrictions on the input files:
1) The "GNSS.txt" is a mandatory file.
2) The InSAR '*Type*' can be realised only by "DInSAR", "SBAS" or "PSI" signature.
3) The number of distinct InSAR '*Orbit*' signatures must be less than or equal to 3.
4) The number of distinct InSAR '*Element*' signatures within particular '*Orbit*' must be less than or equal to 9.
5) The number of distinct InSAR '*Element*' signatures within particular '*Type*' must be less than or equal to 10.

## Headers and data columns structure in the input files:
1. GNSS: `YYYY MM DD X Y Z mX mY mZ`

    | Signature | Type    | Parameter  |
    | :---      | :----:  | :---       |
    | *YYYY*    | `int`   | Year       |
    | *MM*      | `int`   | Month      |
    | *DD*      | `int`   | Day        |
    | *X*       | `float` | Geocentric X coordinate [m] |
    | *Y*       | `float` | Geocentric Y coordinate [m] |
    | *Z*       | `float` | Geocentric Z coordinate [m] |
    | *mX*      | `float` | Error of geocentric X coordinate [m] |
    | *mY*      | `float` | Error of geocentric Y coordinate [m] |
    | *mZ*      | `float` | Error of geocentric Z coordinate [m] |


2. DInSAR: `YYYY1 MM1 DD1 YYYY2 MM2 DD2 DSP INC_ANG HEAD_ANG ERROR`

    | Signature | Type    | Parameter  |
    | :---      | :----:  | :---       |
    | *YYYY1*   | `int`   | Year of primary image    |
    | *YYYY2*   | `int`   | Year of secondary image  |
    | *MM1*     | `int`   | Month of primary image   |
    | *MM2*     | `int`   | Month of secondary image |
    | *DD1*     | `int`   | Day of primary image     |
    | *DD2*     | `int`   | Day of secondary image   |
    | *DSP*     | `float` | LOS displacement [m]     |
    | *INC_ANG* | `float` | Incidence angle [rad]    |
    | *HEAD_ANG*| `float` | Heading angle [rad]      |
    | *ERROR*   | `float` | Error of LOS displacement [m] |

3. SBAS & PSI: `YYYY MM DD DSP INC_ANG HEAD_ANG ERROR`

     **The *ERROR* column can be replaced by: *COH* (`float`): Coherence factor
      The coherence will be converted to the error value expressed in the metric domain using the theory presented in [Hanssen, 2001](https://repository.tudelft.nl/islandora/object/uuid%3Aa83859d5-c034-427e-b6a9-114c4b008d19) and [Tondaś et al., 2023](https://doi.org/10.1007/s00190-023-01789-z).
      To calculate the error using coherence factor the wavelength of the Sentinel-1 is applied.**

[Hanssen, R. (2001).](https://repository.tudelft.nl/islandora/object/uuid%3Aa83859d5-c034-427e-b6a9-114c4b008d19) Radar interferometry: Data interpretation and error analysis.
[Tondaś, D. et al. (2023).](https://doi.org/10.1007/s00190-023-01789-z) Kalman filter-based integration of GNSS and InSAR observations for local nonlinear strong deformations.

