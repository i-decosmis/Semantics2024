import json
import pandas as pd
    
def reset_csv_file():
    df = pd.read_csv('test_scripts/test_five/predictions/predictions.csv')
    df['score'] = df['score'].replace(1, 0)
    df.to_csv('test_scripts/test_five/predictions/reset_predictions.csv', index=False)
                
reset_csv_file()