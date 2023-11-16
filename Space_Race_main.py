import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from iso3166 import countries
from datetime import datetime


data = pd.read_csv("mission_launches.csv")
pd.options.display.float_format = '{:,.2f}'.format

# EXPLORING DATA
data.info()
data.describe()


# CLEANING DATA
data.isna().values.any()
data.duplicated().values.any()
data.dropna(how='all', inplace=True)
data.drop("Unnamed: 0.1", axis=1, inplace=True)
data.drop("Unnamed: 0", axis=1, inplace=True)
data.fillna(0, inplace=True)
data.isna().values.any()


# MANIPULATING DATA
data["Date"] = pd.to_datetime(data["Date"], utc=True)

data.Price = data.Price.str.replace(",", "")
data["Price"] = pd.to_numeric(data["Price"])
data.Price.describe()


# VISUALISING DATA

# Number of Launches per Company
launch_orga = data.groupby("Organisation", 
                           as_index=False).agg({"Date": pd.Series.count}).sort_values(by="Date", ascending=False)

fig_launch = px.bar(x=launch_orga.Organisation,
                    y=launch_orga.Date,
                    color=launch_orga.Date,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    title="Number of Launches per Company")
fig_launch.update_layout(xaxis_title="Organisations", yaxis_title="Number of Launches")
fig_launch.show()

# some numbers: active/retired rockets, successful/failed missions
nr_active = data[data.Rocket_Status == "StatusActive"].count()
nr_retired = data[data.Rocket_Status == "StatusRetired"].count()
nr_success = data[data.Mission_Status == "Success"].count()
nr_failure = data[data.Mission_Status != "Success"].count()
print(f"Number of active rockets: {nr_active.Rocket_Status}")
print(f"Number of active rockets: {nr_retired.Rocket_Status}")
print(f"Number of successful missions: {nr_success.Mission_Status}, Number of failed missions: {nr_failure.Mission_Status}")


# How expensive are Launches?
data_price_no_NaN = data.Price.dropna()

fig_prices = px.histogram(x=data_price_no_NaN.values, nbins=20,
                          title="How expensive are the Launches?")
fig_prices.update_layout(xaxis_title="Price in USD millions",
                         yaxis_title="Number of Launches")
fig_prices.update_traces(marker_color='purple')
fig_prices.show()


# Choropleth map to show the number of launches and failures by country
data.Location.isna().values.any()

countries_list = []
"""creates a list of country codes"""
for country in countries:
    countries_list.append(country)

countries_data = data.Location.count()
country_name = []
"""extracts the country inside the Location column """
for i in range(countries_data):
    name_c = data.Location[i].split(", ")[-1]
    country_name.append(name_c)

    # change old country names
country_name = [c.replace("Russia", "Russian Federation") for c in country_name]
country_name = [c.replace("New Mexico", "USA") for c in country_name]
country_name = [c.replace("Shahrud Missile Test Site", "Iran") for c in country_name]
country_name = [c.replace("Pacific Missile Range Facility", "USA") for c in country_name]
country_name = [c.replace("Barents Sea", "Russian Federation") for c in country_name]
country_name = [c.replace("Gran Canaria", "USA") for c in country_name]
country_name = [c.replace("Yellow Sea", "China") for c in country_name]
country_name = [c.replace("Pacific Ocean", "USA") for c in country_name]
country_name = [c.replace("North Korea", "Korea, Democratic People's Republic of") for c in country_name]
country_name = [c.replace("South Korea", "Korea, Republic of") for c in country_name]
country_name = [c.replace("USA", "United States of America") for c in country_name] 
country_name = [c.replace("Iran", "Iran, Islamic Republic of") for c in country_name] 

new_column_ccode = []
"""creates country codes + adds a new column in DataFrame data"""
for ii in range(len(country_name)):
    for jj in range(len(countries_list)):
        if country_name[ii] in countries_list[jj]:
            new_column_ccode.append(countries_list[jj][2])
data["Country_Code"] = new_column_ccode

len(new_column_ccode)
len(country_name)

# TESTCODE
# unique_list = []
# for x in country_name:
#     if x not in unique_list:
#         unique_list.append(x)
# TESTCODE
# unique_code = []
# for x in new_column_ccode:
#     if x not in unique_code:
#         unique_code.append(x)

missions = data.groupby("Country_Code").agg({"Mission_Status": pd.Series.count})
fig_map = px.choropleth(locations=missions.index,
                        color=missions.Mission_Status,
                        hover_name=missions.index,
                        color_continuous_scale=px.colors.sequential.matter,
                        title="Number of Launches by Country")
fig_map.show()

failed_missions = data[data.Mission_Status == "Failure"]
failures = failed_missions.groupby("Country_Code").agg({"Mission_Status": pd.Series.count})
fig2_map = px.choropleth(locations=failures.index,
                         color=failures.Mission_Status,
                         hover_name=failures.index,
                         color_continuous_scale=px.colors.sequential.deep,
                         title="Number of Failures by Country")
fig2_map.show()


# sunburst chart of the countries, organisations, and mission status.
fig_sun = px.sunburst(data, path=["Country_Code", "Organisation", "Mission_Status"],
                      color="Mission_Status",
                      color_continuous_scale='RdBu',
                      title="Mission Status per Country and Organisation")
fig_sun.show()

# Total amount of money spent by organisation on space missions
total_money = data.groupby("Organisation", as_index=False).agg({
              "Price": pd.Series.sum}).sort_values(by="Price", ascending=False)
total_money.drop(total_money.loc[total_money["Price"] == 0.00].index, inplace=True)

fig_money = px.bar(total_money.sort_values(by="Price", ascending=False),
                   x="Organisation",
                   y="Price",
                   color="Price",
                   color_continuous_scale='RdBu',
                   title="Total Amount of Money Spent by Organisation on Space Missions (in millions USD)")
fig_money.update_layout(yaxis_title="Price in millions USD")
fig_money.show()

# Money spent by organisation per launch
money_orga_launch = data.groupby(["Organisation", "Mission_Status"], as_index=False).agg({"Price": pd.Series.sum})
money_orga_launch.drop(money_orga_launch.loc[money_orga_launch["Price"] == 0.00].index, inplace=True)
money_orga_launch.sort_values(by="Price", ascending=False)

fig_price_launch = px.bar(money_orga_launch.sort_values(by="Price", ascending=False),
                          x="Organisation",
                          y="Price",
                          color="Price",
                          color_continuous_scale='RdBu',
                          title="Total Amount of Money Spent by Organisation per Launch (in millions USD)")
fig_price_launch.update_layout(yaxis_title="Price in millions USD",
                               yaxis=dict(
                                   tickmode='linear',
                                   tick0=5000,
                                   dtick=10000))
fig_price_launch.show()

# launches per year
data["Year"] = data.Date.dt.year
sorted_data = data.sort_values(by="Year")

yearly_launches = sorted_data.Year.value_counts()[data.Year.unique()].sort_index(ascending=True)
fig_year = px.line(x=yearly_launches.index, y=yearly_launches.values, title="Number of Launches per Year")
fig_year.update_layout(xaxis_title="Year", yaxis_title="Total Number of Launches")
fig_year.show()


# launches per month
fig, ax = plt.subplots(figsize=(15, 10))
month = data.Date.dt.month.value_counts().sort_index(ascending=True)
roll_month = month.rolling(window=3).mean()

sns.lineplot(month, ax=ax, color="green", label="Monthly Counts")
ax2 = ax.twinx()
sns.lineplot(roll_month, ax=ax, color="orange", label="Rolling Average")

ax.set_xlabel('Months')
ax.set_ylabel('Number of Launches')
ax.set_title('Total Number of Launches per Month', fontsize=25)
ax.legend()
plt.grid()
plt.show()

# months with the highest number of launches
best_months = data.Date.dt.month.value_counts().sort_values(ascending=False)
print(best_months)

# Variation of launch price over time
data.Price.fillna(0, inplace=True)
data_clean_zeros = data[data['Price'] != 0.00]

mean_prices = data_clean_zeros.groupby("Year", as_index=False).agg({"Price": pd.Series.mean})

price = sns.lineplot(mean_prices, x="Year", y="Price", color="purple")

sns.set_style(style="darkgrid")
plt.xlabel('Years')
plt.ylabel('Average Price in USD millions')
plt.xticks(np.arange(1965, max(mean_prices.Year)+1, 5))
plt.title('Average Money per Year Spent on Space Missions', fontsize=25)
plt.show()

# Top 10 countries with most launches
top_10_organisations = launch_orga[:10]

# Number of launches over time by the top 10 organisations
grouped_df = data.groupby(['Organisation', 'Year'], as_index=False).size()
top_10 = grouped_df.groupby('Organisation', as_index=False)['size'].sum().sort_values(by="size", ascending=False)
list_top10 = top_10.Organisation[:10].to_list()
filtered_orgas = grouped_df[grouped_df["Organisation"].isin(list_top10)]

sns.lineplot(filtered_orgas, x="Year", y="size", hue="Organisation")

sns.set_style(style="darkgrid", rc={'figure.figsize': (12, 8)})
plt.title("Number of Launches over Time by the Top 10 Organisations", fontsize=20)
plt.ylabel("Number of Launches")
plt.xticks(np.arange(1960, max(filtered_orgas.Year)+1, 5))
plt.show()


# Cold war space race
USA_data = data.loc[(data.Country_Code == "USA") & (data.Year <= 1991)]
RUS_data = data.loc[(data.Country_Code == "RUS") & (data.Year <= 1991)].replace("RUS", "USSR")
KAZ_data = data.loc[(data.Country_Code == "KAZ") & (data.Year <= 1991)].replace("KAZ", "USSR")
cold_war = pd.concat([USA_data, RUS_data, KAZ_data])
nr_cold_war = cold_war.groupby("Country_Code", as_index=False).agg({"Mission_Status": pd.Series.count})

fig1_cw = px.pie(nr_cold_war, values="Mission_Status",
                 names="Country_Code",
                 title="Cold War Space Race: Number of Launches of the USSR & USA")
fig1_cw.update_traces(textposition='inside', textinfo='percent+label')
fig1_cw.show()  # compares total number of launches of USSR & USA


yearly_cw = cold_war.groupby(["Country_Code", "Year"], as_index=False).agg({"Mission_Status": pd.Series.count})

sns.lineplot(yearly_cw, x="Year", y="Mission_Status", hue="Country_Code")
plt.title("Cold War: Total Number of Launches per Year and Country", fontsize=15)
plt.ylabel("Number of Launches")
plt.show()  # total number of launches year-on-year by USSR & USA


failures_cw = cold_war[cold_war.Mission_Status != "Success"]
yearly_failures = failures_cw.groupby(["Country_Code", "Year"], as_index=False).agg({"Mission_Status": pd.Series.count})

sns.lineplot(yearly_failures, x="Year", y="Mission_Status", hue="Country_Code")
plt.title("Cold War: Total Number of Mission Failures per Year and Country", fontsize=15)
plt.ylabel("Number of Launches")
plt.show()  # charts total number of failures per year and cold war country


# mission failures
failures_data = data[data.Mission_Status != "Success"]
yearly_fail = failures_data.groupby("Year").agg({"Mission_Status": pd.Series.count})
yearly_launches = data.groupby("Year").agg({"Mission_Status": pd.Series.count})

sns.lineplot(yearly_fail, x="Year", y="Mission_Status", color="red")
plt.title("Total Number of Mission Failures per Year", fontsize=15)
plt.ylabel("Number of Launches")
plt.show()  # mission failures per year


pct_yearly_fail = (yearly_fail.Mission_Status/yearly_launches.Mission_Status) * 100

sns.lineplot(x=pct_yearly_fail.index, y=pct_yearly_fail.values, color="darkred")
plt.title("Precentage of Mission Failures per Year", fontsize=15)
plt.ylabel("Percentage of Failures")
plt.show()  # # mission failures per year in percent

# Lead countries in terms of total number of launches
grouped_df = data.groupby(["Country_Code", "Year"], as_index=False).size()
result_df = grouped_df.loc[grouped_df.groupby('Year')['size'].idxmax()]

sns.barplot(result_df, x="Year", y="size", hue="Country_Code")
plt.title("Lead Country in Terms of Total Number of Launches per Year", fontsize=20)
plt.ylabel("Number of Launches")
plt.xticks(rotation=90)
plt.show()  # lead country per year by total number of launches


success_data = data[data.Mission_Status == "Success"]
grouped_success = success_data.groupby(["Country_Code", "Year"], as_index=False).size()
result_success = grouped_success.loc[grouped_success.groupby('Year')['size'].idxmax()]

sns.barplot(result_success, x="Year", y="size", hue="Country_Code")
plt.title("Lead Country in Terms of Total Number of Successful Missions per Year", fontsize=20)
plt.ylabel("Number of successful Launches")
plt.xticks(rotation=90)
plt.show()  # lead country per year by successful missions


