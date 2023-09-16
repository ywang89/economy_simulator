import matplotlib.pyplot as plt
import seaborn as sns

def plot_wealth(econ):
    plt.plot(econ.run_days, econ.tot_wealth, marker='o')
    plt.xlabel("Days")
    plt.ylabel("Total wealth (in money)")
    plt.title("Total wealth of the economy over time")
    plt.show()

def plot_compare_econ(econs:dict, figsize=(7, 3)):
    fig, axes = plt.subplots(figsize=figsize)

    n = len(econs)

    for k, curr_econ in econs.items():
        axes.plot(curr_econ.run_days, curr_econ.tot_wealth, marker='o',
                  label=k)
        
    axes.set_xlabel("Days")
    axes.set_ylabel("Total wealth (in money)")
    axes.set_title("Total wealth of the economy over time")
    axes.legend()
    
    plt.close(fig)
    return fig

def plot_person(person):
    person.df_tot_amt.plot(marker='o')