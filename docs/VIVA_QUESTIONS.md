# Viva Questions and Answers

1. **What is the project about?**  
   It is an analytics prototype for patient-flow forecasting and draft hospital staff scheduling.

2. **Why is patient-flow analysis useful?**  
   It helps understand demand patterns, peak periods and department workloads.

3. **What is machine learning?**  
   A field where algorithms learn patterns from data to make predictions or decisions.

4. **Which ML algorithm is used?**  
   Random Forest Regressor.

5. **Why Random Forest?**  
   It combines multiple decision trees and can model nonlinear relationships with limited preprocessing.

6. **What is regression?**  
   A supervised learning task used to predict numeric values.

7. **What is the target variable?**  
   Patient count.

8. **Which features are used?**  
   Weekday, month, day of year, weekend indicator and department code.

9. **What is MAE?**  
   Mean Absolute Error, the average absolute difference between actual and predicted values.

10. **What is RMSE?**  
    Root Mean Squared Error, which penalizes larger errors more strongly.

11. **Why use a chronological split?**  
    It avoids training on future observations when evaluating past-to-future prediction.

12. **What is synthetic data?**  
    Artificially generated data used for testing and demonstration.

13. **Why synthetic data here?**  
    To avoid exposing confidential patient information.

14. **What is Streamlit?**  
    A Python framework for building interactive data applications.

15. **What is SQLite?**  
    A lightweight relational database stored in a local file.

16. **What is Pandas used for?**  
    Data cleaning, transformation, grouping and analysis.

17. **What is Plotly used for?**  
    Interactive charts and visualizations.

18. **What is patient inflow?**  
    The number of patients arriving or being registered over a period.

19. **What is staff requirement forecasting?**  
    Estimating staffing needs from expected demand and configured staffing ratios.

20. **What is shift optimization in this prototype?**  
    A draft allocation of available staff to shifts based on department and role demand.

21. **Is the scheduler globally optimal?**  
    No. It uses a greedy heuristic and reports unfilled positions.

22. **What is a greedy algorithm?**  
    An algorithm that makes a locally suitable choice at each step.

23. **What is a database table?**  
    A structured collection of records with defined columns.

24. **Why validate CSV files?**  
    To catch missing columns and invalid values before importing data.

25. **What are the limitations?**  
    Synthetic data, baseline forecasting and simplified scheduling constraints.

26. **Can it be deployed in a real hospital now?**  
    No. It needs validation, security review, privacy controls and clinical/operational expert input.

27. **What is overfitting?**  
    When a model learns training data too closely and performs poorly on unseen data.

28. **What is feature engineering?**  
    Creating useful input variables from raw data.

29. **What is a KPI?**  
    A key performance indicator used to monitor an important measure.

30. **What future improvements are possible?**  
    Real approved data evaluation, richer scheduling constraints, model comparison, authentication and secure integration.
