import pandas as pd

def main(input_file_path, output_file_path, first_lower_bound, upper_bounds):

    # file_path = "Raw Data/Tally-2.xlsx" #convert to take input

    sheet_name = 'Sheet1' 

    def read_and_clean_sheet(file_path, sheet_name):
        
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Remove company details
        header_row = df[df.iloc[:, 0] == 'Date'].index[0]
        cleaned_df = pd.read_excel(file_path, sheet_name=sheet_name, header=[header_row, header_row + 1])
        
        # Merge header rows
        cleaned_df.columns = [f'{i} {j}'.strip() if j != 'nan' else i for i, j in cleaned_df.columns]

        # Delete unwanted columns
        columns_to_drop = ['Particulars Unnamed: 1_level_1', 'Vch Type Unnamed: 2_level_1', 'Vch No. Unnamed: 3_level_1', 'Closing Quantity', 'Closing Rate', 'Closing Value', 'Inwards Value', 'Outwards Value']
        cleaned_df = cleaned_df.drop(columns=columns_to_drop)

        # Create a new combined Rate column
        cleaned_df['Rate'] = cleaned_df['Inwards Rate'].fillna(cleaned_df['Outwards Rate'])

        # Delete Inwards and Outwards Rate Columns
        cleaned_df = cleaned_df.drop(columns=['Inwards Rate', 'Outwards Rate'])

        # Rename columns
        cleaned_df = cleaned_df.rename(columns={
            'Inwards Quantity': 'Inward',
            'Outwards Quantity': 'Outward',
            'Rate': 'Rate',
            'Date Unnamed: 0_level_1': 'Date',
        })  
        
        # List of columns in the desired order
        new_column_order = ['Date', 'Rate', 'Inward', 'Outward']

        # Reorder the DataFrame columns
        cleaned_df = cleaned_df[new_column_order]
        cleaned_df = cleaned_df.dropna(subset=['Date'])
        cleaned_df['Inward'] = pd.to_numeric(cleaned_df['Inward'], errors='coerce').fillna(0)
        cleaned_df['Outward'] = pd.to_numeric(cleaned_df['Outward'], errors='coerce').fillna(0)

        return cleaned_df


    df = read_and_clean_sheet(input_file_path, sheet_name)
    print(df.head())


    ############################################################################################################
    # Divide the data based on ranges

    # Function to generate continuous ranges with overlap
    def generate_continuous_ranges(lower_bound, high_values):
        ranges = []
        
        for high in high_values:
            ranges.append((lower_bound, high))  # Save the range as a tuple
            lower_bound = high  # Set the next lower bound to be exactly the current high value
        
        ranges.append((lower_bound, None))  # The final range starts from the last lower bound and goes onwards
        print(f"Ranges: {ranges}")
        return ranges

    # Function to check for values outside the specified ranges
    def check_outside_ranges(df, ranges):
        condition = pd.Series([False] * len(df))
        for low, high in ranges:
            if high is not None:
                condition |= (df['Rate'] >= low) & (df['Rate'] < high)  # Change to [low, high) range
            else:
                condition |= (df['Rate'] >= low)
        
        outside_ranges = df[~condition]
        ignored_rates = outside_ranges['Rate'].unique()
        
        return ignored_rates

    # Function to divide data into sheets by rate range and save to a new Excel file
    def divide_and_save_by_rate(df, file_path, ranges):
        with pd.ExcelWriter(file_path) as writer:
            for i, (low, high) in enumerate(ranges):
                sheet_name = f"Range_{low}-{high if high is not None else 'above'}"
                if high is not None:
                    sheet_df = df[(df['Rate'] >= low) & (df['Rate'] < high)]  # Change to [low, high) range
                else:
                    sheet_df = df[df['Rate'] >= low]
                
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        print(f"Data divided and saved into sheets in {file_path}")


    # lower_bound = int(input("Enter the starting stock rate: "))
    # high_values = list(map(int, input("Enter the upper bounds of the ranges, separated by spaces: ").split()))

    continuous_ranges = generate_continuous_ranges(first_lower_bound, upper_bounds)

    ignored_rates = check_outside_ranges(df, continuous_ranges)
    print(f"Ignored rates: {ignored_rates}")

    # output_file_path = "Divided_Data_By_Rate.xlsx"
    divide_and_save_by_rate(df, output_file_path, continuous_ranges)

if __name__ == "__main__":
    main()

