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

Below is a look at the feature importance plot:

<img width="1898" height="1090" alt="image" src="https://github.com/user-attachments/assets/17c06a6f-7b28-4f57-9400-a82f56bcfdf1" />

### iVB Over Expected Model

As mentioned earlier, the motivation for this model stemmed from the anticipated importance of its relationship with pitch location. Generally, pitchers with higher iVB perform better at the top of the strike zone, and vice versa. However, there are nuances that can make this relationship non-linear. Because the model is ultimately trained on run values derived from hitters’ decisions, it was important to account for the element of deception—what the batter perceives from the pitcher.

For example, a fastball with 13 iVB could perform better at the top of the zone than one with 18 iVB, due to other pitch characteristics that hitters subconsciously recognize. In this way, the model also helped quantify deception as part of the analysis. When selecting features, I focused on variables that reflect both what the hitter can see and what the pitcher can control.
#### Features
- Release Speed
- Spin Rate
- Arm Angle
- Release Position z
- Release Position x
- Extension
#### Results
For this model, I leveraged the Optuna package for hyperparameter optimization and used XGBoost to build the predictive model. The best iteration for predicting iVB achieved an RMSE of 3.8. While the RMSE could likely have been improved with additional or more complex features, I chose to prioritize interpretability by focusing on variables that reflect what the hitter can see and what the pitcher can control.

Below is a look at the feature importance results:

<img width="951" height="545" alt="image" src="https://github.com/user-attachments/assets/df2890c5-f6ce-4036-80f0-f826c400360b" />

### Location Model

After building the initial model components, I turned to the final and most important piece of this project. The objective was to train a model on both pitch characteristics and location in order to quantify the value of any pitch in any situation. The response variable for this model was the run value of a pitch outcome, conditioned on count, using data from the MLB level.

Once trained, this model allows us to fix a pitcher’s average pitch characteristics and then simulate 100,000 randomized pitch locations. By holding pitch characteristics constant, we can isolate how pitch value varies solely as a function of location. 
#### Features
- Release Speed
- Release position x, z
- Arm angle
- Extension
- Platoon State
- Count
- Break (Horizontal and Vertical)
- iVB over expected
- Spin Rate
- Spin Axis
- Vertical Approach Angle
#### Results
For this model I wanted to go with a boosting model like Catboost because of it's ability to capture some of the complicated, non-linear relationships between the pitch charactersitics and location. The run time with Catboost was also enhanced in comparison to some of the other boosting models I tried out.

Below is a look at the feature importance plot

## App Output

Now that we have the model to predict based on pitch characteristics and location, we can now plot these predictions and have a better idea of what pitches perform well and where. Here is an example of what the output looks like in a count neutral setting.

<img width="1058" height="351" alt="image" src="https://github.com/user-attachments/assets/eff2dfc0-c0f7-4300-8842-9414cd76425a" />






