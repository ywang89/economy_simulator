import matplotlib.pyplot as plt
import seaborn as sns


def _plot_econ_item(df_farmer, df_taylor, item, ax):
    ax.plot(item, data=df_farmer, label='farmer')
    ax.plot(item, data=df_taylor, label='taylor')
    ax.legend()
    ax.set_title(item)

def plot_econ(econ, figsize=(21, 6)):
    '''Plots visualizations of an economy.
    '''
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
    item_list = ['gold', 'food', 'cloth', 'fert', 'leaf']
    len_item_list = len(item_list)
    for i, ax in enumerate(axes.flat):
        if i > len_item_list - 1:
            break
        _plot_econ_item(
            df_farmer=econ.farmer.df_tot_amt,
            df_taylor=econ.taylor.df_tot_amt,
            item=item_list[i],
            ax=ax
        )
    plt.close(fig)
    return fig

def plot_wealth(econ):
    plt.plot(econ.run_days, econ.tot_wealth, marker='o')
    plt.xlabel("Days")
    plt.ylabel("Total wealth (in money)")
    plt.title("Total wealth of the economy over time")
    plt.show()

def plot_compare_econ(econs:dict, figsize=(7, 3), marker=None):
    fig, axes = plt.subplots(figsize=figsize)

    n = len(econs)

    for k, curr_econ in econs.items():
        axes.plot(curr_econ.run_days, curr_econ.tot_wealth, marker=marker,
                  label=k)
        
    axes.set_xlabel("Days")
    axes.set_ylabel("Total wealth (in money)")
    axes.set_title("Total wealth of the economy over time")
    axes.legend()
    
    plt.close(fig)
    return fig

def plot_person(person):
    person.df_tot_amt.plot(marker='o')