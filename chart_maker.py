import mongo
import matplotlib.pyplot as plt
import datetime

def PSAtimeline(patientnumber="MB0389PR"):
    doc = mongo.retrieveDoc(patientnumber)
    psas = [list(item) for item in zip(doc['PSAs'].keys(), doc['PSAs'].values())]
    deltaTs = [(datetime.datetime.strptime(psas[iii][0], "%Y-%m-%d") - datetime.datetime.strptime(psas[0][0], "%Y-%m-%d")).days for iii, item in enumerate(psas)]
    # setup chart
    fig, ax = plt.subplots()
    ax.bar([item for item in deltaTs], [item[1] for item in psas], width=10, color='y')
    ax.set_ylabel('ng/mL')
    ax.set_title('PSA level by date')
    ax.set_xticks(deltaTs)
    ax.set_xticklabels([str(item[0]) for item in psas], rotation=90)
    plt.show()

if __name__ == "__main__":
    PSAtimeline()
