# Simulation Based Modeling For Optimal Pitch Locations (College Level)
Streamlit link: Private Data Used; Screenshots will be included

## Process

Pitch-level values are not a new phenomenon in the public baseball space, but they can be especially useful when examining the factors that drive them and identifying where they are most predictable. In this project, a pitch-level value model is leveraged that incorporates both pitch characteristics and location. To isolate the effect of pitch location, we fixed each pitcher’s pitch characteristics at their respective averages and then simulated 100,000 random pitch locations, predicting outcomes under these constant characteristics.

## Modeling

This project leverages three separate models: (1) pitcher arm angle at the college level (CatBoost), (2) induced vertical break (iVB) over expected (XGBoost), and (3) a final run-value model (CatBoost). The arm angle and iVB over expected models feed into the run-value model, which also incorporates various additional variables.

The motivation for including arm angle and iVB over expected comes from their critical role in determining pitch value relative to location. These models introduce meaningful signal that may help explain variation in pitch-level run value attributable to location—signal that might otherwise be missed without explicitly modeling these inputs.

### Pitcher Arm Angle Model

Because Major League Baseball and Baseball Savant had come out with arm angle for MLB players, this allowed us to train off of that and apply that model on the college level. Here were the input features used in the arm angle model:
##### Features
- release position x
- release position z
- extension
- player height
- interaction term (release position z * release extension * player height)
##### Results
To start, I tested a basic linear regression model under the assumption that the relationship between variables was approximately linear. The model achieved an RMSE of 6.68 when predicting arm angle. I then leveraged CatBoost in combination with the Optuna hyperparameter optimization package in Python, which improved performance to an RMSE of 4.99. Given this improvement, I selected CatBoost as the final model.



