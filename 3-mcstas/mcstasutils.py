import mcstasscript as ms


def plot(
    data,
    var1="th",
    var2="t",
    t_bins=200,
    orders_of_mag=5,
    log=True,
    left_lim=[-170, 10],
    right_lim=[-10, 170],
    **kwargs,
):
    event1 = ms.name_search("Banana_large_0", data)
    event2 = ms.name_search("Banana_large_1", data)

    bins1 = (200, t_bins)
    bins2 = (200, t_bins)

    ev2 = event2.make_2d(var1, var2, n_bins=bins2)
    ev2.set_xlabel("theta [deg]")

    ev1 = event1.make_2d(var1, var2, n_bins=bins1)
    ev1.set_xlabel("theta [deg]")

    ms.make_sub_plot(
        [
            ev2,
            ev1,
        ],
        orders_of_mag=orders_of_mag,
        log=log,
        left_lim=left_lim,
        right_lim=right_lim,
        **kwargs,
    )
