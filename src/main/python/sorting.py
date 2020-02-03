#CREATING CSV FILE

# Insert Manual Price
# Insert Percentage Markup
# Change to PRODUCT CLASS

# FOR GREASES TRANSFORM KG per PCS in LT/PCS
# MERGE ROTTERDAM LUBES WITH GREASES
# INSERT Manual Price
# INSERT Percentage markup
# Change to PRODUCT CLASS


import pandas as pd

#       Category        Class
# sorting_order can accept both a list of strings or a single string as its value

sorting_order = {
    'MOTORCYCLE OIL':              'MCO',
    'PASSENGER CAR MOTOR OIL':    'PCMO',
    'GEAR AND TRANSMISSION OIL':   'TRO',
    'DIESEL ENGINE OIL':           'DEO',
    'MARINE OIL':                  'MAR',
    'SPECIALTY FLUID':             'SPE',
    'GREASES':                ' GREASE ',
    'HYDRAULIC SYSTEM OIL':        'HSO',
    'INDUSTRIAL GEAR OIL':         'IGO',
    'COMPRESSOR AND TURBINE OIL':  'CTO',
    'OTHER INDUSTRIAL OIL':        'IND',
    'METAL WORKING FLUID':         'MWF'
}

old_sorting_order = {'MOTORCYCLE LUBRICANTS': ['MCEO-4T', 'MCEO-2T', 'AF', 'FORK'],
                 'PASSENGER CAR, MPV, SUV AND LIGHT COMMERCIAL VEHICLE OILS': ['PCMO'],
                 'AUTOMOTIVE GEARBOX AND TRANSMISSION OILS': ['AGO', 'DCT', 'ATF', 'UTTO'],  # Ignore 'HYDR', 'UTTO'],
                 'HEAVY DUTY DIESEL ENGINE OILS': ['DEO'],
                 'STATIONARY AND RAILROAD ENGINE OILS': ['GAS', 'GEN', 'LM'],
                 'MARINE OILS': ['MARINE'],
                 'BRAKE FLUIDS AND COOLANTS': ['BF'],  # ignore for now 'AF'],
                 'LUBRICATING GREASES': ['GREASE'],
                 'HYDRAULIC SYSTEMS OILS': ['HYDR'],
                 'INDUSTRIAL GEARBOX OILS': ['IGO'],
                 'TURBINE AND COMPRESSOR OILS': ['COMP', 'TUR', 'SLIDE/HYDR'],
                 'ROCKDRILL AND CHAINSAW OILS': ['RD', 'TAC'],
                 'TRANSFORMER OILS': ['TRANSFORMER'],
                 'WHITE OILS': ['WHITE'],
                 'METALWORKING FLUIDS': ['NCUT'],
                 'HEAT TRANSFER OILS': ['HT'],
                 'OTHER': ['AGO-UTTO', 'CIRCUL', 'CVT', 'DEO-STOU', 'OUTBOARD-2T', 'OUTBOARD-4T', 'SLIDE',
                           'COMPRESSOR']}


def sort_df(df):
    class_list = list()

    for key in sorting_order:
        for item in sorting_order[key]:
            if type(item) == list:
                class_list.append(item)
            else:
                class_list.append(sorting_order[key])

    seen = []

    for i in class_list:
        if i in seen:
            pass
        else:
            seen.append(i)

    df['PRODUCT CLASS'] = pd.Categorical(df['PRODUCT CLASS'], seen)

    df = df.sort_values(['PRODUCT CLASS', 'SYSPRO CODE', 'SPECIFICATION LEVEL', 'LT/PCS'], ascending=[1, 1, 0, 0])

    return df

def categorize(df):

    # Splits a dataframe sorted by class into different dataframes of the same class
    # Returns a dictionary with keys corresponding to the category of that dataframe
    # and with values dataframes with that class

    dataframes = {}

    for k in sorting_order:

        if type(sorting_order[k]) == str:

            class_df = df.loc[df["PRODUCT CLASS"] == sorting_order[k]]

            if not class_df.empty:

                dataframes[k] = class_df

        else:

            for prod_class in sorting_order[k]:
                print(prod_class)
                class_df = df.loc[df["PRODUCT CLASS"] == prod_class]
                if not class_df.empty:
                    dataframes[k] = class_df

    if dataframes == {}:
        raise Exception('MissingSortedData')

    return dataframes
