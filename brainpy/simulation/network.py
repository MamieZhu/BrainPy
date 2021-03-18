# -*- coding: utf-8 -*-

from collections import OrderedDict

from brainpy import backend
from brainpy import profile
from brainpy.simulation import population
from brainpy.simulation import utils

__all__ = [
    'Network',
]


class Network(object):
    """The main simulation controller in ``BrainPy``.

    ``Network`` handles the running of a simulation. It contains a set
    of objects that are added with `add()`. The `run()` method actually
    runs the simulation. The main loop runs according to user add orders.
    The objects in the `Network` are accessible via their names, e.g.
    `net.name` would return the `object`.
    """

    def __init__(self, *args, show_code=False, **kwargs):
        # record the current step
        self.t_start = 0.
        self.t_end = 0.

        # store all nodes
        self.all_nodes = OrderedDict()

        # store the step function
        self.run_func = None
        self.show_code = show_code

        # add nodes
        self.add(*args, **kwargs)

    def __getattr__(self, item):
        if item in self.all_nodes:
            return self.all_nodes[item]
        else:
            return super(Network, self).__getattribute__(item)

    def _add_obj(self, obj, name=None):
        # 1. check object type
        if not isinstance(obj, population.Population):
            raise ValueError(f'Unknown object type "{type(obj)}". '
                             f'Currently, Network only supports '
                             f'{population.NeuGroup.__name__} and '
                             f'{population.TwoEndConn.__name__}.')
        # 2. check object name
        name = obj.name if name is None else name
        if name in self.all_nodes:
            raise KeyError(f'Name "{name}" has been used in the network, '
                           f'please change another name.')
        # 3. add object to the network
        self.all_nodes[name] = obj
        if obj.name != name:
            self.all_nodes[obj.name] = obj

    def add(self, *args, **kwargs):
        """Add object (neurons or synapses) to the network.

        Parameters
        ----------
        args
            The nameless objects.
        kwargs
            The named objects, which can be accessed by `net.xxx`
            (xxx is the name of the object).
        """
        for obj in args:
            self._add_obj(obj)
        for name, obj in kwargs.items():
            self._add_obj(obj, name)

    def run(self, duration, inputs=(), report=False, report_percent=0.1):
        """Run the simulation for the given duration.

        This function provides the most convenient way to run the network.
        For example:

        Parameters
        ----------
        duration : int, float, tuple, list
            The amount of simulation time to run for.
        inputs : list, tuple
            The receivers, external inputs and durations.
        report : bool
            Report the progress of the simulation.
        report_percent : float
            The speed to report simulation progress.
        """
        # preparation
        start, end = utils.check_duration(duration)
        dt = profile.get_dt()
        ts = backend.arange(start, end, dt)

        # build the network
        run_length = ts.shape[0]
        format_inputs = utils.format_net_level_inputs(inputs, run_length)
        net_runner = backend.get_net_runner()(all_nodes=self.all_nodes)
        self.run_func = net_runner.build(run_length=run_length,
                                         formatted_inputs=format_inputs,
                                         return_code=False,
                                         show_code=self.show_code)

        # run the network
        utils.run_model(self.run_func, times=ts, report=report, report_percent=report_percent)

        # end
        self.t_start, self.t_end = start, end

    @property
    def ts(self):
        """Get the time points of the network.
        """
        return backend.arange(self.t_start, self.t_end, profile.get_dt())
