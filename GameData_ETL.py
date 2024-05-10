from game_data import GameData

if __name__ == "__main__":
    # Create Object
    gd = GameData()
    
    # Extract data
    df_list = gd.extract()
    
    # Transform data
    gd.merge_data(df_list)
    
     # Load df to csv
    df = gd.get_main_df()
    df.to_csv('transformed_game_data.csv', index=False)