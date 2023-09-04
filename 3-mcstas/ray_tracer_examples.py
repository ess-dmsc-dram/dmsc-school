import simple_simulator


def guide():
    sim = simple_simulator.Simulator()

    src = sim.add_component("Source", width=0.1, height=0.1, angle_spread=3)

    guide = sim.add_component("Guide", width=0.07, height=0.07, length=4, position=[0,0,0.25])

    monitor = sim.add_component("Monitor", nx=20, ny=20, width=0.08, height=0.08,
                                position=[0,0,guide.length + 0.8], relative=guide)

    return sim


def large():
    sim = simple_simulator.Simulator()

    src = sim.add_component("Source", width=0.1, height=0.1, angle_spread=3)

    guide = sim.add_component("Guide", width=0.07, height=0.07, length=2, position=[0,0,0.25])

    mirror_angle = 30
    mirror1 = sim.add_component("Mirror", width=0.04, height=0.06,
                                position=[0,0, guide.length + 0.25],
                                rotation=[0, mirror_angle, 0], relative=guide)

    arm1 = sim.add_component("Arm", rotation=[0, mirror_angle, 0], relative=mirror1)

    mirror2 = sim.add_component("Mirror", width=0.04, height=0.06,
                                position=[0,0, 0.25],
                                rotation=[0, 180-mirror_angle, 0], relative=arm1)

    arm2 = sim.add_component("Arm", rotation=[0, 180-mirror_angle, 0], relative=mirror2)

    monitor = sim.add_component("Monitor", nx=20, ny=20, width=0.05, height=0.05,
                                position=[0,0,1], relative=arm2)


    return sim
    
