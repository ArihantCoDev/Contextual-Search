import pandas as pd
import sys

# Load the dataset
input_file = 'sample_products_500.csv'
output_file = 'sample_products_500_fixed.csv'

try:
    df = pd.read_csv(input_file)
    
    # Identify Headphones currently in Accessories
    mask = (df['category'] == 'Accessories') & (df['title'].str.contains('Headphone', case=False))
    
    count = mask.sum()
    print(f"Found {count} headphones in 'Accessories'. Moving them to 'Electronics'...")
    
    # Update category
    df.loc[mask, 'category'] = 'Electronics'
    
    # Save back to CSV
    df.to_csv(output_file, index=False)
    print(f"Fixed data saved to {output_file}")
    
except Exception as e:
    print(f"Error: {e}")
