#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 15:30:50 2025

@author: gauthierberanger
"""

import pandas as pd
import numpy as np

# Charger le dataset
file_path = "/Users/gauthierberanger/Documents/power-optimisation/charger_power_output.csv"
df = pd.read_csv(file_path)

# Convertir meter_value_at en datetime et extraire l'heure
df['meter_value_at'] = pd.to_datetime(df['meter_value_at'])
df['hour'] = df['meter_value_at'].dt.floor('H')

# Garder les max de power_kw pour chaque connector_id de chaque charger_id de chaque meter_id pour chaque heure
df_max = df.groupby(['meter_id', 'charger_id', 'connector_id', 'hour'])['power_kw'].max().reset_index()

# Regrouper les données pour obtenir la somme des max par meter_id pour chaque heure
df_summed = df_max.groupby(['meter_id', 'hour'])['power_kw'].sum().reset_index()

# Sauvegarde des résultats
df_max.to_csv("/Users/gauthierberanger/Documents/power-optimisation/processed_max_power.csv", index=False)
df_summed.to_csv("/Users/gauthierberanger/Documents/power-optimisation/processed_summed_power.csv", index=False)

print("Processing complete. Files saved: processed_max_power.csv and processed_summed_power.csv")

# Fonction pour extraire les données d'un meter_id
def extract_meter_data(meter_id, df):
    return df[df['meter_id'] == meter_id]

# Fonction d'optimisation du contracted power
def optimize_contracted_power(meter_data):
    possible_powers = np.linspace(meter_data['power_kw'].min(), meter_data['power_kw'].max(), 100)
    best_power = None
    best_cost = float('inf')
    
    for contracted_power in possible_powers:
        x = (meter_data['power_kw'] > contracted_power).sum()
        cost = 16.44 * contracted_power + 11.75 * x
        
        if cost < best_cost:
            best_cost = cost
            best_power = contracted_power
    
    return best_power


'''
for i in range(1, 1000):  # Boucle sur les indices 1 à 99
    if i in df_summed.index:  # Vérifie que l'index existe
        meter_id = df_summed.loc[i, df_summed.columns[0]]  # Récupère l'ID du compteur
        print(meter_id)  # Affiche l'ID réel
        print(optimize_contracted_power(extract_meter_data(meter_id, df_summed)))  # Utilisation correcte de meter_id
 '''       
        



# Calcul du contracted power optimal pour chaque meter_id
meter_ids = df_summed['meter_id'].unique()
optimal_powers = {meter_id: optimize_contracted_power(extract_meter_data(meter_id, df_summed)) for meter_id in meter_ids}

df_optimal_power = pd.DataFrame(list(optimal_powers.items()), columns=['meter_id', 'optimal_contracted_power'])

# Calcul des coûts annuels
def calculate_total_cost(meter_id, df_summed, optimal_power):
    meter_data = extract_meter_data(meter_id, df_summed)
    x = (meter_data['power_kw'] > optimal_power).sum()
    fixed_cost = 199.8 + 255.84
    variable_cost = 16.44 * optimal_power + 11.75 * x
    return fixed_cost + variable_cost

# Application du calcul pour chaque station
df_optimal_power['total_annual_cost'] = df_optimal_power.apply(lambda row: calculate_total_cost(row['meter_id'], df_summed, row['optimal_contracted_power']), axis=1)

# Sauvegarde des résultats
df_optimal_power.to_csv("/Users/gauthierberanger/Documents/power-optimisation/optimal_contracted_power.csv", index=False)

print("Optimal contracted power and total annual costs calculated and saved to optimal_contracted_power.csv")

print(df_optimal_power['total_annual_cost'].sum())  # coût total 




# Charger le dataset sous-optimal
file_path = "/Users/gauthierberanger/Documents/power-optimisation/energy_connections.csv"
df = pd.read_csv(file_path)

df_sous_optimal_power = df.iloc[:, :2]


df_sous_optimal_power['total_annual_cost'] = df_sous_optimal_power.apply(lambda row: calculate_total_cost(row['meter_id'], df_summed, row['subscribed_power_value_kva']), axis=1)

print(df_sous_optimal_power['total_annual_cost'].sum())  # coût total 
