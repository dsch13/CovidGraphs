import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

Dummy = plt.figure()
DPI = Dummy.get_dpi()
plt.close()
pd.options.mode.chained_assignment = None


# Useful for getting country from JHU data
country = 'Country/Region'


# Acquires and cleans Global JHU data from the url passed
def CleanJHU_Global(url):
    df = pd.read_csv(url)
    df = df.drop(columns=['Province/State', 'Lat', 'Long'])

    return df.groupby(country).sum()


# Acquires and cleansUS JHU data from the url passed
def CleanJHU_US(url):
    df = pd.read_csv(url)
    return df.drop(columns=['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Lat', 'Long_'])


GD_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
         '/csse_covid_19_time_series/time_series_covid19_deaths_global.csv '

GC_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
         '/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

USD_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
          '/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'

USC_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
          '/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'


# Reads NYT data, and handles date information
def Read_NYT():
    NYT_url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"

    df = pd.read_csv(NYT_url)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df


NYT = Read_NYT()


# Picks the 10 states with the most cases
# Useful for graph readability
def select_States():
    newDate = NYT.loc[NYT['date'] == NYT['date'].max()]
    return newDate.nlargest(10, columns=['cases'])['state'].tolist()


def make_NYT_Graph(attribute, log):
    plt.close()
    fig, ax = plt.subplots()
    fig.set_size_inches(1024/float(DPI), 512/float(DPI))
    mostRecent = NYT['date'].max()
    mostRecent = mostRecent.strftime('%x')

    mostCases = select_States()
    for state in mostCases:
        stateData = NYT.loc[NYT['state'] == state]
        baseDate = stateData.loc[NYT['deaths'] >= 10]['date'].min()
        stateData['time since'] = (stateData['date'] - baseDate).dt.days
        stateData = stateData.loc[stateData['time since'] >= 0]
        ax.plot('time since', attribute, data=stateData, label=state)

    ax.set_xlabel('Days since 10th death')
    ax.set_ylabel(attribute.capitalize())
    if log:
        ax.set_yscale('log')
        fName = 'NYT_'+attribute+'-log'
    else:
        fName = 'NYT_'+attribute
    ax.set_title('Total Covid '+attribute.capitalize()+' by State')
    # plt.subplots_adjust(left=0.15)
    plt.legend()
    plt.grid()
    plt.figtext(.3, .0, "Twitter-@CovidPublicData | Data- @NYT https://github.com/nytimes/covid-19-data", fontsize=8)
    plt.figtext(.1, .0, 'Most recent data from '+str(mostRecent), color='blue', fontsize=8)
    # plt.show()
    plt.savefig('graphs\\'+fName, bbox_inches='tight')
    plt.close()


Global_deaths = CleanJHU_Global(GD_url).reset_index()
Global_cases = CleanJHU_Global(GC_url).reset_index()


def select_Countries():
    newDate = Global_cases.columns[-1]
    return Global_cases.nlargest(10, columns=[newDate])[country].to_list()


def make_JHU_graph(attribute, log):
    plt.close()
    fig, ax = plt.subplots()
    fig.set_size_inches(1024 / float(DPI), 512 / float(DPI))
    mostCases = select_Countries()
    mostRecent = Global_cases.columns[-1]

    for c in mostCases:
        countryData = Global_cases.loc[Global_cases[country] == c]
        countryData = countryData.transpose().reset_index().iloc[1:, :]\
            .rename(columns={'index': 'date', countryData.index[0]: 'cases'})
        countryData['date'] = countryData['date'].apply(lambda d: pd.to_datetime(d))

        countryDeaths = Global_deaths.loc[Global_deaths[country] == c]
        countryDeaths = countryDeaths.transpose().reset_index().iloc[1:, :]\
            .rename(columns={'index': 'date', countryData.index[0]: 'deaths'})
        countryDeaths['date'] = countryDeaths['date'].apply(lambda d: pd.to_datetime(d))

        baseDate = pd.to_datetime(countryDeaths.loc[countryDeaths.iloc[:, -1] >= 10].iloc[0, 0])

        countryData['timeSince'] = (countryData['date'] - baseDate).dt.days
        countryDeaths['timeSince'] = (countryDeaths['date'] - baseDate).dt.days

        if attribute == 'cases':
            df = countryData
        else:
            df = countryDeaths

        df = df.loc[df['timeSince'] >= 0]

        ax.plot(df['timeSince'], df.iloc[:, 1], label=c)

    ax.set_xlabel('Days since 10th death')
    ax.set_ylabel(attribute.capitalize())
    if log:
        ax.set_yscale('log')
        fName = 'JHU_' + attribute + '-log'
    else:
        fName = 'JHU_' + attribute
    ax.set_title('Total Covid ' + attribute.capitalize() + ' by Country')
    # plt.subplots_adjust(left=0.15)
    plt.legend()
    plt.grid()
    plt.figtext(.3, .0, "Twitter-@CovidPublicData | Data- @JHUSystems https://github.com/CSSEGISandData/COVID-19",
                fontsize=8)
    plt.figtext(.1, .0, 'Most recent data from ' + str(mostRecent), color='blue', fontsize=8)
    # plt.show()
    plt.savefig('Graphs\\'+fName, bbox_inches='tight')
    plt.close()


def makeStateGraph(state):
    stateData = NYT.loc[NYT['state'] == state]
    stateData.to_csv('Data\\NYT_'+state+'-Data.csv')
