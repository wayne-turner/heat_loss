# heat_loss

Designed as an educational toolkit for calculating and analyzing heat loss in buildings. Capable of estimating heat loss and associated costs, this project caters to a wide audience including homeowners, builders, and energy analysts. While it provides tools for practical analysis, it is also crafted with educators, students, and DIY enthusiasts in mind, offering a solid starting point for learning and experimentation in the field of thermal dynamics and building design.


## Motivation
The project was born out of a need to tackle high winter energy costs in a family member's historic home. As a General Contractor, I sought to quantify the ROI of various energy-saving upgrades. This toolkit empowers users to make informed decisions about improving their homes' thermal efficiency, blending practical solutions with educational resources to address energy loss in any building.

## Applications

- **Energy Audits**: Evaluate building performance and identify opportunities for insulation upgrades.
- **Cost Analysis**: Estimate heating costs under different scenarios to inform budgeting and energy-saving measures.
- **Building Design**: Assist in selecting materials and designs for new constructions or renovations to maximize thermal efficiency.

## How Others Can Use This Repository

- **Educators and Students**: A resource for teaching and learning about thermal dynamics in building design.
- **DIY Homeowners**: Plan energy efficiency improvements and understand the impact of various insulation strategies.
- **General Contractors**: Offer detailed analyses and recommendations for reducing heating costs and improving building performance.

## Features

- Calculation of specific heat loss for customized building configurations.
- Scenario analysis across a range of roof materials, window types, and insulation R-values.
- Detailed output including total heat loss in kWh and total cost, facilitating in-depth analysis and decision-making.

## Quick Start

1. Clone the repository to your local machine.
2. Ensure you have Python and Pandas installed.
3. Import the functions from `heat_loss_simulation.py` into your Python script or notebook.
4. Call the `compute_specific_heat_loss` or `heat_loss_scenarios` functions with desired parameters.

Example:
```python
from heat_loss_simulation import compute_specific_heat_loss

results = compute_specific_heat_loss(sqft_roof=2000, ...)
```




## Dependencies
- `Python 3.6`  or newer
- `Pandas` 
- `Matplotlib`  or `Seaborn` (Optional)




## Parameter Reference

| Argument               | Type    | Default Value | Description                                                                                                                                                                                                                                                               |
|------------------------|---------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sqft_roof`            | float   | 1800          | Square footage of the roof.                                                                                                                                                                                                                                               |
| `sqft_walls`           | float   | 1500          | Square footage of the walls.                                                                                                                                                                                                                                              |
| `roof_material_type`   | str     | 'asphalt'     | Type of material used for the roof. Options: 'asphalt', 'wood', 'metal', 'tile'.                                                                                                                                                                                          |
| `wall_material_type`   | str     | 'wood'        | Type of material used for the walls. Options: 'brick', 'concrete', 'wood'.                                                                                                                                                                                                |
| `ambient_temp_F`       | float   | 50            | Ambient temperature in Fahrenheit.                                                                                                                                                                                                                                        |
| `T_inside_F`           | float   | 70            | Interior temperature in Fahrenheit.                                                                                                                                                                                                                                       |
| `duration_hours`       | int     | 24            | Duration of the heat loss calculation in hours.                                                                                                                                                                                                                           |
| `insulation_r_value`   | str     | 'R13-R15'     | Insulation R-value category. Options: 'R13-R15', 'R16-R21', 'R22-R33', 'R34-R60'. Defaults to 'R13-R15'.                                                                                                                                                                   |
| `air_changes_per_hour` | float   | 0.5           | Air changes per hour. Typical range for residential buildings is 0.1 to 1.0 ACH.                                                                                                                                                                                          |
| `window_area_sqft`     | float   | 500           | Area of windows in square feet.                                                                                                                                                                                                                                           |
| `window_type`          | str     | 'double'      | Type of window. Options: 'single', 'double', 'triple'. Defaults to 'double'.                                                                                                                                                                                              |
| `electricity_cost_per_kWh` | float   | 0.12          | Cost of electricity per kWh. Typical range in the U.S. is $0.08 to $0.20 per kWh.                                                                                                                                                                                        |

## Material Properties and Ranges

### Roofing and Wall Materials

| Material        | Average Thickness (mm) | Thickness for Calculations (m) | Thermal Conductivity (W/m·K) | Range                                  |
|-----------------|------------------------|--------------------------------|-------------------------------|----------------------------------------|
| Asphalt Shingles| 3 to 12                | 0.005                          | 0.17 to 0.24                  | Thickness range useful for calculations.|
| Wood Shingles   | 6 to 20                | 0.01                           | 0.12 to 0.04                  | Broad range due to wood type variations.|
| Metal Roofing   | 0.4 to 1.5             | 0.0007                         | Varies widely                 | Steel: 15 to 50, Aluminum: 205 to 250, Copper: ~385. Consider specific metal type.|
| Tile Roofing    | Clay: 10 to 20, Concrete: up to 50 | Clay: 0.015, Concrete: 0.03 | 0.7 to 1.3                    | Clay and concrete tiles differ significantly in thickness and thermal properties.|

### Window Types

| Type    | U-Value (W/m²K) | Range                            |
|---------|-----------------|----------------------------------|
| Single  | 5.7             | Least energy-efficient.          |
| Double  | 2.8             | Moderate energy efficiency.      |
| Triple  | 1.6             | Most energy-efficient.           |

### Insulation R-Values

| Category   | R-Value | Range                               |
|------------|---------|-------------------------------------|
| R13-R15    | 14      | Common for exterior walls.          |
| R16-R21    | 18      | Higher efficiency, thicker insulation.|
| R22-R33    | 28      | Used in colder climates for enhanced insulation.|
| R34-R60    | 47      | Very high efficiency, used in extreme climates or specialized applications.|

### Air Changes Per Hour (ACH)

Typical residential buildings have an ACH ranging from 0.1 to 1.0, indicating the air volume exchange rate with the outside environment. The chosen default of 0.5 ACH is a balance between energy efficiency and indoor air quality.

### Electricity Cost

The cost of electricity per kWh typically ranges from $0.08 to $0.20 in the U.S., subject to fluctuations based on energy markets, geographical location, and policy changes. The default value of $0.12 per kWh is a median figure intended for general calculations.





## Usage

The `compute_specific_heat_loss` function computes the total heat loss and the associated cost for a building over a specified duration.

```python
results = compute_specific_heat_loss(
    sqft_roof=2000,
    sqft_walls=1600,
    roof_material_type='metal',
    wall_material_type='brick',
    ambient_temp_F=45,
    T_inside_F=75,
    duration_hours=24,
    insulation_r_value='R22-R33',
    air_changes_per_hour=0.7,
    window_area_sqft=600,
    window_type='triple',
    electricity_cost_per_kWh=0.15
)
```

The `heat_loss_scenarios` function allows you to calculate heat loss and associated costs for a variety of scenarios, essentially providing a rank order ROI.

```python
results = heat_loss_scenarios(
    sqft_roof=2000,
    sqft_walls=1600,
    ambient_temp_F=45,
    T_inside_F=75,
    duration_hours=24,
    air_changes_per_hour=0.7,
    window_area_sqft=600,
    electricity_cost_per_kWh=0.15
)
```

# Output

The `heat_loss_scenarios()` function generates a comprehensive DataFrame that presents calculated total heat loss (in kilowatt-hours, kWh) and the associated cost for a variety of scenarios. These scenarios differ by combinations of roof materials, window types, and insulation R-values, with optional inputs for specific building parameters (sample below):

| Roof Material | Insulation R-Value | Window Type | Total Cost ($) | Total Heat Loss (kWh) |
|---------------|---------------------|-------------|----------------|-----------------------|
| wood          | R34-R60             | triple      | 1.13           | 9.40                  |
| wood          | R34-R60             | double      | 1.13           | 9.41                  |
| wood          | R34-R60             | single      | 1.13           | 9.42                  |
| ...           | ...                 | ...         | ...            | ...                   |
| metal         | R13-R15             | double      | 3.52           | 29.37                 |
| metal         | R13-R15             | single      | 3.53           | 29.38                 |


### Interpreting the Results

1. **Energy Efficiency Insights**: `Q_total_kWh` column shows the total energy lost through the building envelope over the specified duration. Lower values indicate better insulation and window choices, resulting in less heat loss and higher energy efficiency.

2. **Cost Implications**: `total_cost` column provides an estimate of the financial impact of the heat loss. It is calculated based on the `Q_total_kWh` and the `electricity_cost_per_kWh`, giving you an idea of how different materials and insulation levels can affect your heating bills.

3. **Material and Insulation Comparison**: By examining rows with different `roof_material_type`, `wall_material_type`, `window_type`, and `insulation_r_value`, you can compare how each factor contributes to heat loss and cost. This can guide decisions in construction or renovations to achieve desired thermal performance and cost-effectiveness.

4. **Optimization Opportunities**: Sorting the DataFrame by `Q_total_kWh` or `total_cost` can help identify which combinations of materials and insulation values offer the best performance for your specific conditions (ambient temperature, desired interior temperature, etc.).

5. **Customization for Specific Needs**: Adjusting the input parameters (e.g., square footage, temperature settings) allows for tailored analysis reflecting your unique situation, providing personalized insights into potential energy savings and cost reductions.






## Conclusion

Beyond immediate practical applications, this repository is intended predominantly for educational purposes. It encourages users to delve into the mechanics of heat loss, providing a groundwork upon which further research, innovation, and exploration can be built.

