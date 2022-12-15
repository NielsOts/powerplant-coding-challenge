from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
import json
from types import SimpleNamespace


# the API port specifics

app = Flask(__name__)
api = Api(app)
port = 8888
host = '0.0.0.0'

# create a object powerplant


class PowerPlant:
    def __init__(self, name, pmin, pmax, cost, efficiency):
        self.name = name
        self.pmin = int(pmin)
        self.pmax = int(pmax)
        self.cost = float(cost)
        self.ce = cost/efficiency
        self.p = 0


rest = 0
ce_list = []
index = ["pp1", "pp2", "pp3", "pp4"]
columns = ['id', 'name', 'pmin', 'pmax', 'ce', 'cost', 'p']


class WindFarm:
    def __init__(self, name, pmin, pmax, efficiency):
        self.name = name
        self.pmin = int(pmin)
        self.pmax = int(pmax)
        self.p = float((efficiency*pmax)/100)

# make a post request to the API


@app.route('/productionplan', methods=['POST'])
def process_json():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = request.json
        pp1 = PowerPlant(data["powerplants"][0]["name"],
                         data["powerplants"][0]["pmin"],
                         data["powerplants"][0]["pmax"],
                         data["fuels"]["gas(euro/MWh)"],
                         data["powerplants"][0]["efficiency"]
                         )
        pp2 = PowerPlant(data["powerplants"][1]["name"],
                         data["powerplants"][1]["pmin"],
                         data["powerplants"][1]["pmax"],
                         data["fuels"]["gas(euro/MWh)"],
                         data["powerplants"][1]["efficiency"]
                         )
        pp3 = PowerPlant(data["powerplants"][2]["name"],
                         data["powerplants"][2]["pmin"],
                         data["powerplants"][2]["pmax"],
                         data["fuels"]["gas(euro/MWh)"],
                         data["powerplants"][2]["efficiency"]
                         )
        pp4 = PowerPlant(data["powerplants"][3]["name"],
                         data["powerplants"][3]["pmin"],
                         data["powerplants"][3]["pmax"],
                         data["fuels"]["kerosine(euro/MWh)"],
                         data["powerplants"][3]["efficiency"]
                         )
        wf1 = WindFarm(data["powerplants"][4]["name"],
                       data["powerplants"][4]["pmin"],
                       data["powerplants"][4]["pmax"],
                       data["fuels"]["wind(%)"]
                       )
        wf2 = WindFarm(data["powerplants"][5]["name"],
                       data["powerplants"][5]["pmin"],
                       data["powerplants"][5]["pmax"],
                       data["fuels"]["wind(%)"]
                       )
        load = data["load"]

        responseDf = pd.DataFrame(
            {'name': [wf1.name, wf2.name, pp1.name, pp2.name, pp3.name, pp4.name], 'p': [0, 0, 0, 0, 0, 0]})

        df = pd.DataFrame({'name': [pp1.name, pp2.name, pp3.name, pp4.name],
                           'pmin': [pp1.pmin, pp2.pmin, pp3.pmin, pp4.pmin],
                           'pmax': [pp1.pmax, pp2.pmax, pp3.pmax, pp4.pmax], 'cost': [pp1.cost, pp2.cost, pp3.cost, pp4.cost], 'ce': [pp1.ce, pp2.ce, pp3.ce, pp4.ce], 'p': [pp1.p, pp2.p, pp3.p, pp4.p]}, columns=columns, index=index)

        # return str(df.name)
        if (load-wf1.p-wf2.p-pp1.pmax-pp2.pmax-pp3.pmax-pp4.pmax) > 0:
            return "Not enough power to meet requirement"

        # check if wf1 is sufficient and exact
        elif (load-wf1.p) == 0:
            # return str(responseDf.loc[responseDf["name"] == wf1.name])
            responseDf.loc[responseDf["name"] == wf1.name, "p"] = load

            return "only wf 1 " + str(responseDf)

        # check if wf2 is sufficient and exact
        elif (load-wf2.p) == 0:
            responseDf.loc[responseDf["name"] == wf2.name, "p"] = load
            return "only wf 2" + str(responseDf)

         # check if wf1 and wf2 is sufficient and exact
        elif (load-wf1.p-wf2.p) == 0:
            responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
            responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
            return "wf1 and wf2" + str(responseDf)

         # wf1 and wf2 do not supply enough so other pp are needed
        elif (load-wf1.p-wf2.p) > 0:
            # the rest load is the load still required after both windfarms are active
            rest = load-wf1.p-wf2.p

            # sort the dataframe according to their cost efficiency to decide on the order to produce the extra power
            df = df.sort_values("ce")

            # check if the first pp produces enough power to match the remaining load, if so, no other pp is needed
            if (rest - df.iloc[0].pmax) <= 0:
                # tc = df.iloc[0].cost*rest
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = rest
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
                return responseDf.to_json(orient='records')

            # the first pp does not produce enough power to match the remaining load, check if pp2 produces enough power to meet remaining load
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = rest - df.iloc[0].pmax
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] == df['name'].iloc[2], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax - df.iloc[3].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[2], "p"] = df['pmax'].iloc[2]
                responseDf.loc[responseDf["name"] == df['name'].iloc[3], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
                return responseDf.to_json(orient='records')

        elif (load-wf1.p) > 0:
            rest = load-wf1.p
            df = df.sort_values("ce")

            if (rest - df.iloc[0].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = rest
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p

                return responseDf.to_json(orient='records')

            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               pp2.name, "p"] = rest - df.iloc[0].pmax
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
                return responseDf.to_json(orient='records')

            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] == df['name'].iloc[2], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p
                return responseDf.to_json(orient='records')

            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax - df.iloc[3].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[2], "p"] = df['pmax'].iloc[2]
                responseDf.loc[responseDf["name"] == pp4.name, "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax
                responseDf.loc[responseDf["name"] == wf1.name, "p"] = wf1.p

                return responseDf.to_json(orient='records')

        elif (load-wf2.p) > 0:
            rest = load-wf2.p
            df = df.sort_values("ce")

            if (rest - df.iloc[0].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = rest
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p

                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = rest - df.iloc[0].pmax
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] == df['name'].iloc[2], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p
                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax - df.iloc[3].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[2], "p"] = df['pmax'].iloc[2]
                responseDf.loc[responseDf["name"] == df['name'].iloc[3], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax
                responseDf.loc[responseDf["name"] == wf2.name, "p"] = wf2.p

                return responseDf.to_json(orient='records')

        else:
            rest = load
            df = df.sort_values("ce")

            if (rest - df.iloc[0].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = rest

                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = rest - df.iloc[0].pmax

                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] == df['name'].iloc[2], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax

                return responseDf.to_json(orient='records')
            elif (rest - df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax - df.iloc[3].pmax) <= 0:
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[0], "p"] = df['pmax'].iloc[0]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[1], "p"] = df['pmax'].iloc[1]
                responseDf.loc[responseDf["name"] ==
                               df['name'].iloc[2], "p"] = df['pmax'].iloc[2]
                responseDf.loc[responseDf["name"] == df['name'].iloc[3], "p"] = rest - \
                    df.iloc[0].pmax - df.iloc[1].pmax - df.iloc[2].pmax

                return responseDf.to_json(orient='records')

    else:
        return 'Content-Type not supported!'


if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
