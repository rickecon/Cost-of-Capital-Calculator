"""
SOI Auxiliary Script (soi_processing.py):
-------------------------------------------------------------------------------
Module that handles reading in the soi data (corporate, partners, and sole proprietorships). Makes calls to a different
script for each one of these entities. Also provides auxiliary scripts to format the partner and proprietorship dataframes and to
interpolate missing data.
Last updated: 7/26/2016.

"""
# Import packages
import os.path
import sys
import numpy as np
import pandas as pd
# Import custom modules
import pull_soi_corp as corp
import pull_soi_partner as prt
import pull_soi_proprietorship as prop
# Factor used to adjust dollar values
_FILE_FCTR = 10**3

def pull_soi_data():
    """Creates a dictionary that is updated with the soi entity data after each method.

        :returns: DataFrames organized by entity type (corp, partner, sole prop)
        :rtype: dictionary
    """
    entity_dfs = {}
    entity_dfs.update(corp.load_corp_data())

    entity_dfs.update(prt.load_partner_data(entity_dfs))

    entity_dfs.update(prop.load_proprietorship_data(entity_dfs))

    print entity_dfs.keys()
    c_corp_sector = entity_dfs['c_corp'][(entity_dfs['c_corp']['Codes:']>9)
                                       & (entity_dfs['c_corp']['Codes:']<100)]
    c_corp_major = entity_dfs['c_corp'][(entity_dfs['c_corp']['Codes:']>99)
                                       & (entity_dfs['c_corp']['Codes:']<1000)]
    c_corp_minor = entity_dfs['c_corp'][(entity_dfs['c_corp']['Codes:']>99999)
                                       & (entity_dfs['c_corp']['Codes:']<1000000)]
    s_corp_sector = entity_dfs['s_corp'][(entity_dfs['s_corp']['Codes:']>9)
                                       & (entity_dfs['s_corp']['Codes:']<100)]
    s_corp_major = entity_dfs['s_corp'][(entity_dfs['s_corp']['Codes:']>99)
                                       & (entity_dfs['s_corp']['Codes:']<1000)]
    s_corp_minor = entity_dfs['s_corp'][(entity_dfs['s_corp']['Codes:']>99999)
                                       & (entity_dfs['s_corp']['Codes:']<1000000)]
    part_sector = entity_dfs['part_data'][(entity_dfs['part_data']['Codes:']>9)
                                       & (entity_dfs['part_data']['Codes:']<100)]
    part_sector.drop_duplicates(subset=['Codes:'],inplace=True)
    part_major = entity_dfs['part_data'][(entity_dfs['part_data']['Codes:']>99)
                                       & (entity_dfs['part_data']['Codes:']<1000)]
    part_major.drop_duplicates(subset=['Codes:'],inplace=True)
    part_minor = entity_dfs['part_data'][(entity_dfs['part_data']['Codes:']>99999)
                                       & (entity_dfs['part_data']['Codes:']<1000000)]
    part_minor.drop_duplicates(subset=['Codes:'],inplace=True)
    sp_sector = entity_dfs['sole_prop_data'][(entity_dfs['sole_prop_data']['Codes:']>9)
                                       & (entity_dfs['sole_prop_data']['Codes:']<100)]
    sp_major = entity_dfs['sole_prop_data'][(entity_dfs['sole_prop_data']['Codes:']>99)
                                       & (entity_dfs['sole_prop_data']['Codes:']<1000)]
    sp_minor = entity_dfs['sole_prop_data'][(entity_dfs['sole_prop_data']['Codes:']>99999)
                                       & (entity_dfs['sole_prop_data']['Codes:']<1000000)]
    c_corp_sector.to_csv('c_corp_sector.csv',encoding='utf-8')
    c_corp_major.to_csv('c_corp_major.csv',encoding='utf-8')
    c_corp_minor.to_csv('c_corp_minor.csv',encoding='utf-8')
    s_corp_sector.to_csv('s_corp_sector.csv',encoding='utf-8')
    s_corp_major.to_csv('s_corp_major.csv',encoding='utf-8')
    s_corp_minor.to_csv('s_corp_minor.csv',encoding='utf-8')
    part_sector.to_csv('part_sector.csv',encoding='utf-8')
    part_major.to_csv('part_major.csv',encoding='utf-8')
    part_minor.to_csv('part_minor.csv',encoding='utf-8')
    sp_sector.to_csv('sp_sector.csv',encoding='utf-8')
    sp_major.to_csv('sp_major.csv',encoding='utf-8')
    sp_minor.to_csv('sp_minor.csv',encoding='utf-8')
    quit()

    df03_sector = df03[(df03['Codes:']>9) & (df03['Codes:']<100)]
    df03_major = df03[(df03['Codes:']>99) & (df03['Codes:']<1000)]
    df03_minor = df03[(df03['Codes:']>99999) & (df03['Codes:']<1000000)]

    # make one big data frame - by industry and entity type



    return entity_dfs


def format_dataframe(df, crosswalk):
    """Formats the dataframe with industry codes as the rows and asset information as the columns.

        :param df: The dataframe to be formatted
        :param crosswalk: Maps the SOI codes to their respective industries
        :type df: DataFrame
        :type crosswalk: DataFrame
        :returns: A clean dataframe with the data easily acessible
        :rtype: DataFrame
    """
    indices = []
    # Removes the extra characters from the industry names
    for string in df.index:
        indices.append(string.replace('\n',' ').replace('\r',''))
    # Adds the industry names as the first column in the dataframe
    df.insert(0,indices[0],indices)
    # Stores the values of the first row in columns
    columns = df.iloc[0].tolist()
    # Drops the first row because it will become the column labels
    df = df[df.Item != 'Item']
    # Removes extra characters from the column labels
    for i in xrange(0,len(columns)):
        columns[i] = columns[i].strip().replace('\r','')
    # Sets the new column values
    df.columns = columns
    # Creates a new index based on the length of the crosswalk (needs to match)
    df.index = np.arange(0,len(crosswalk['Codes:']))
    # Inserts the codes from the crosswalk as the second column in the df
    df.insert(1,'Codes:',crosswalk['Codes:'])
    names = df['Item']
    codes = df['Codes:']
    # Multiplies the entire dataframe by a factor of a thousand
    df = df * _FILE_FCTR
    # Replaces the industry names and codes to adjust for the multiplication in the previous step
    df['Item'] = names
    df['Codes:'] = codes
    # Returns the newly formatted dataframe
    return df


def interpolate_data(entity_dfs, df):
    """Fills in the missing values using the proportion of corporate industry values

        :param entity_dfs: Contains all the soi data by entity type
        :param df: The datframe that will be updated with new values
        :type entity_dfs: dictionary
        :type df: DataFrame
        :returns: The new dataframe with values for all the industries
        :rtype: DataFrame
    """
    # Takes the total corp values as the baseline
    base_df = entity_dfs['tot_corp']
    # Stores the dataframe in a numpy array
    corp_data = np.array(base_df)
    # Stores the partner or prop data in a numpy array
    prt_data = np.array(df)
    # Iterates over each industry in the partner or prop data
    for i in xrange(0, len(prt_data)):
        # If it is a two digit code then it will appear in the denominator of the following calcs
        if(len(str(int(prt_data[i][0]))) == 2):
            # Grabs the parent data from the corporate array
            parent_ind = corp_data[i]
            # Grabs the partner or prop data as well
            prt_ind = prt_data[i][1:]
        # If the partner or prop data is missing a value
        if(prt_data[i][1] == 0):
            # Grabs the corporate data for the minor industry
            corp_ind = corp_data[i]
            # Divides the minor industry corporate data by the major industry data
            ratios = corp_ind / parent_ind
            # Mulitplies the partner or prop data for the major data to find minor partner data
            new_data = prt_ind * ratios[1:]
            # Sets new values in the partner or prop dataframe
            df.set_value(i, 'Fixed Assets', new_data[0])
            df.set_value(i, 'Inventories', new_data[1])
            df.set_value(i, 'Land', new_data[2])
    # Returns the partner or prop dataframe with all the missing values filled in
    return df
