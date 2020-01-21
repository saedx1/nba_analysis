"""
A module that contains functions to perform plots.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.colors import LinearSegmentedColormap

COLOR_LIST = [
    [0.14509804, 0.27843137, 0.46666667],
    [0.25490196, 0.48235294, 0.69411765],
    [0.70588235, 0.84705882, 0.90588235],
    [1.0, 0.99607843, 0.77647059],
    [0.94509804, 0.69019608, 0.43137255],
    [0.7372549, 0.18823529, 0.15686275],
]
CMAP = LinearSegmentedColormap.from_list("my_map", COLOR_LIST, N=60)


def draw_court(ax=None, color="black", lw=2, outer_lines=False):
    """
    Credit to Savvas Tjortjoglou:
    http://savvastjortjoglou.com/nba-shot-sharts.html
    As the title suggest, this draws an nba court on a plot.
    """
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)

    # Create free throw top arc
    top_free_throw = Arc(
        (0, 142.5),
        120,
        120,
        theta1=0,
        theta2=180,
        linewidth=lw,
        color=color,
        fill=False,
    )
    # Create free throw bottom arc
    bottom_free_throw = Arc(
        (0, 142.5),
        120,
        120,
        theta1=180,
        theta2=0,
        linewidth=lw,
        color=color,
        linestyle="dashed",
    )
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle(
        (-250, -47.5), 30, 140, linewidth=lw, color=color, fill=False
    )
    corner_three_b = Rectangle(
        (220, -47.5), 30, 140, linewidth=lw, color=color, fill=False
    )
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc(
        (0, 0), 478, 478, theta1=22.5, theta2=157.5, linewidth=lw, color=color
    )

    # Center Court
    center_outer_arc = Arc(
        (0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color
    )
    center_inner_arc = Arc(
        (0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color
    )

    # List of the court elements to be plotted onto the axes
    court_elements = [
        hoop,
        backboard,
        outer_box,
        inner_box,
        top_free_throw,
        bottom_free_throw,
        restricted,
        corner_three_a,
        corner_three_b,
        three_arc,
        center_outer_arc,
        center_inner_arc,
    ]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle(
            (-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False
        )
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    ax.tick_params(
        axis="both",
        which="both",
        bottom=False,
        top=False,
        left=False,
        right=False,
        labelleft=False,
        labelbottom=False,
    )

    ax.set_xlim(-250, 250)
    ax.set_ylim(422.5, -47.5)

    return ax


def plot_scatter_shots(
    made_x,
    made_y,
    missed_x=None,
    missed_y=None,
    ax=None,
    figure_size=(11, 11),
    **ax_kwargs
):
    """
    Credit to Savvas Tjortjoglou:
    http://savvastjortjoglou.com/nba-shot-sharts.html
    """
    if ax is None:
        ax = plt.gca()

    def_kwargs = dict(
        marker0="o", color0="green", s0=100, marker1="x", color1="red", s1=100
    )
    kwargs0 = {k[:-1]: v for k, v in def_kwargs.items() if k[-1] == "0"}
    kwargs1 = {k[:-1]: v for k, v in def_kwargs.items() if k[-1] == "1"}

    for k, v in ax_kwargs.items():
        if k[-1] == "0":
            kwargs0.update({k[:-1]: v})
        elif k[-1] == "1":
            kwargs1.update({k[:-1]: v})

    ax.scatter(made_x, made_y, **kwargs0)

    if missed_x is not None and missed_y is not None:
        ax.scatter(missed_x, missed_y, **kwargs1)

    draw_court(ax)

    ax.figure.set_size_inches(figure_size)
    ax.set_facecolor((0.93, 0.93, 0.93))

    return ax


def plot_hex_shots(x, y, ax=None, figure_size=(13.8, 11), **ax_kwargs):
    """
    Credit to Savvas Tjortjoglou:
    http://savvastjortjoglou.com/nba-shot-sharts.html
    """
    if ax is None:
        ax = plt.gca()

    # 4 Extreme points are added to make sure that
    # the hexagons are ALWAYS the same size
    x = np.append(np.asanyarray(x), [-255, 255, 255, -255])
    y = np.append(np.asanyarray(y), [422.5, -47.5, 422.5, -47.5])

    def_kwargs = dict(gridsize=(30, 20), cmap=CMAP)
    def_kwargs.update(ax_kwargs)

    hb = ax.hexbin(x, y, **def_kwargs)
    plt.colorbar(hb)

    draw_court(ax)

    ax.figure.set_size_inches(figure_size)
    ax.set_facecolor((0.14509804, 0.27843137, 0.46666667))

    return ax
