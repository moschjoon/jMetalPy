import matplotlib.pyplot as plt
import numpy as np
from statsmodels.sandbox.stats.multicomp import get_tukeyQcrit


def NemenyiCD(alpha: float, num_alg, num_dataset):
    """ Computes Nemenyi's critical difference:

    * CD = q_alpha * sqrt(num_alg*(num_alg + 1)/(6*num_prob))

    where q_alpha is the critical value, of the Studentized range statistic divided by sqrt(2).

    :param alpha: {0.05, 0.01}. Significance level.
    :param num_alg: number of tested algorithms.
    :param num_dataset: Number of problems/datasets where the algorithms have been tested.
    """

    # Get critical value
    q_alpha = get_tukeyQcrit(k=num_alg, df=num_alg * (num_dataset - 1), alpha=alpha) / np.sqrt(2)

    # Compute the critical difference
    cd = q_alpha * np.sqrt(num_alg * (num_alg + 1) / (6.0 * num_dataset))

    return cd


def ranks(data: np.array):
    """ Computes the rank of the elements in data.

    :param data: 2-D matrix
    :return: ranks, where ranks[i][j] == rank of the i-th row w.r.t the j-th column.
    """

    k, n_samples = data.shape

    # Compute ranks. (ranks[i][j] == rank of the i-th treatment on the j-th sample.)
    ranks = np.ones((k, n_samples))
    for j in range(n_samples):
        values, indices, rep = np.unique(
            (-1) * np.sort(-data[:, j]), return_index=True, return_counts=True, )
        for i in range(k):
            ranks[i, j] += indices[values == data[i, j]] + \
                           0.5 * (rep[values == data[i, j]] - 1)

    return ranks


def CDplot(results: np.array, alpha: float = 0.05, alg_names: list = None):
    """ CDgraph plots the critical difference graph show in Janez Demsar's 2006 work:

    * Statistical Comparisons of Classifiers over Multiple Data Sets.

    :param results: A 2-D array containing results from each algorithm. Each row of 'results' represents an algorithm, and each column a dataset.
    :param alpha: {0.05, 0.01}. Significace level for the critical difference.
    :param alg_names: Names of the tested algorithms.
    """

    def _join_alg(avranks, num_alg, cd):
        """
        join_alg returns the set of non significant methods
        """

        # get all pairs
        sets = (-1) * np.ones((num_alg, 2))
        for i in range(num_alg):
            elements = np.where(np.logical_and(
                avranks - avranks[i] > 0, avranks - avranks[i] < cd))[0]
            if elements.size > 0:
                sets[i, :] = [avranks[i], avranks[elements[-1]]]
        sets = np.delete(sets, np.where(sets[:, 0] < 0)[0], axis=0)

        # group pairs
        group = sets[0, :]
        for i in range(1, sets.shape[0]):
            if sets[i - 1, 1] < sets[i, 1]:
                group = np.vstack((group, sets[i, :]))

        return group

    # Initial Checking
    if type(results) == list:
        results = np.asarray(results)
    if alpha not in [0.01, 0.05]:
        raise Exception('Initialization ERROR: In CDplot(...) alpha must be 0.01 0 or 0.05')
    if results.ndim == 2:
        num_alg, num_dataset = results.shape
    else:
        raise Exception('Initialization ERROR: In CDplot(...) results must be 2-D array')
    if alg_names is None:
        alg_names = np.array(
            [r'$m_{' + str(cn + 1) + '}$' for cn in range(num_alg)])
    else:
        alg_names = np.array(alg_names)
    print(results, type(results))
    # Get the critical difference
    cd = NemenyiCD(alpha, num_alg, num_dataset)

    # Compute ranks. (ranks[i][j] rank of the i-th algorithm on the j-th dataset.)
    rranks = ranks(results)

    # Compute for each algorithm the ranking averages.
    avranks = np.mean(rranks, axis=1)
    indices = np.argsort(avranks).astype(np.uint8)
    avranks = avranks[indices]

    # Split algorithms.
    spoint = np.round(num_alg / 2.0).astype(np.uint8)
    leftalg = avranks[:spoint]
    rightalg = avranks[spoint:]
    rows = np.ceil(num_alg / 2.0).astype(np.uint8)

    # Figure settings.
    highest = np.ceil(np.max(avranks)).astype(np.uint8)  # highest shown rank
    lowest = np.floor(np.min(avranks)).astype(np.uint8)  # lowest shown rank
    width = 6  # default figure width (in inches)
    height = (0.375 * (rows + 1))  # figure height

    """
                        FIGURE
      (1,0)
        +-----+---------------------------+-------+
        |     |                           |       |
        |     |                           |       |
        |     |                           |       |
        +-----+---------------------------+-------+ stop
        |     |                           |       |
        |     |                           |       |
        |     |                           |       |
        |     |                           |       |
        |     |                           |       |
        |     |                          |       |
        +-----+---------------------------+-------+ sbottom
        |     |                           |       |
        +-----+---------------------------+-------+
            sleft                       sright     (0,1)
    """

    stop, sbottom, sleft, sright = 0.65, 0.1, 0.15, 0.85

    # Main horizontal axis length
    lline = sright - sleft

    # Initialize figure
    fig = plt.figure(figsize=(width, height), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    # Main horizontal axis
    ax.hlines(stop, sleft, sright, color='black', linewidth=0.7)
    for xi in range(highest - lowest + 1):
        # Plot mayor ticks
        ax.vlines(x=sleft + (lline * xi) / (highest - lowest),
                  ymin=stop, ymax=stop + 0.05, color='black', linewidth=0.7)
        # Mayor ticks labels
        ax.text(x=sleft + (lline * xi) / (highest - lowest),
                y=stop + 0.06,
                s=str(lowest + xi), ha='center', va='bottom')
        # Minor ticks
        if xi < highest - lowest:
            ax.vlines(x=sleft + (lline * (xi + 0.5)) / (highest - lowest),
                      ymin=stop, ymax=stop + 0.025, color='black', linewidth=0.7)

    # Plot lines/names for left models
    vspace = 0.5 * (stop - sbottom) / (spoint + 1)
    for i in range(spoint):
        ax.vlines(x=sleft + (lline * (leftalg[i] - lowest)) / (highest - lowest),
                  ymin=sbottom + (spoint - 1 - i) * vspace, ymax=stop, color='black', linewidth=0.7)
        ax.hlines(y=sbottom + (spoint - 1 - i) * vspace, xmin=sleft,
                  xmax=sleft +
                       (lline * (leftalg[i] - lowest)) / (highest - lowest),
                  color='black', linewidth=0.7)
        ax.text(x=sleft - 0.01, y=sbottom + (spoint - 1 - i) * vspace,
                s=alg_names[indices][i], ha='right', va='center')

    # Plot lines/names for right models
    vspace = 0.5 * (stop - sbottom) / (num_alg - spoint + 1)
    for i in range(num_alg - spoint):
        ax.vlines(x=sleft + (lline * (rightalg[i] - lowest)) / (highest - lowest),
                  ymin=sbottom + i * vspace, ymax=stop, color='black', linewidth=0.7)
        ax.hlines(y=sbottom + i * vspace,
                  xmin=sleft +
                       (lline * (rightalg[i] - lowest)) / (highest - lowest),
                  xmax=sright, color='black', linewidth=0.7)
        ax.text(x=sright + 0.01, y=sbottom + i * vspace,
                s=alg_names[indices][spoint + i], ha='left', va='center')

    # Plot critical difference rule
    ax.hlines(y=stop + 0.2, xmin=sleft, xmax=sleft +
                                             (cd * lline) / (highest - lowest), linewidth=1.5)
    ax.text(x=sleft + 0.5 * (cd * lline) /
              (highest - lowest), y=stop + 0.21, s='CD=%.3f' % cd, ha='center', va='bottom')

    # Get pair of non-significant methods
    nonsig = _join_alg(avranks, num_alg, cd)
    left_lines = nonsig[:np.round(nonsig.shape[0] / 2.0).astype(np.uint8), :]
    right_lines = nonsig[np.round(nonsig.shape[0] / 2.0).astype(np.uint8):, :]

    # plot from the left
    vspace = 0.5 * (stop - sbottom) / (left_lines.shape[0] + 1)
    for i in range(left_lines.shape[0]):
        ax.hlines(y=stop - (i + 1) * vspace,
                  xmin=sleft + lline * (left_lines[i, 0] -
                                        lowest - 0.025) / (highest - lowest),
                  xmax=sleft + lline * (left_lines[i, 1] - lowest + 0.025) / (highest - lowest), linewidth=2)
    # plot from the right
    vspace = 0.5 * (stop - sbottom) / (left_lines.shape[0])
    for i in range(right_lines.shape[0]):
        ax.hlines(y=stop - (i + 1) * vspace,
                  xmin=sleft + lline * (right_lines[i, 0] -
                                        lowest - 0.025) / (highest - lowest),
                  xmax=sleft + lline * (right_lines[i, 1] - lowest + 0.025) / (highest - lowest), linewidth=2)

    plt.show()