# -*- coding: utf-8 -*-

from typing import Union

import brainpy.math as bm
from brainpy.dyn.base import Container, CondNeuGroup, Channel, check_master
from brainpy.types import Shape

__all__ = [
  'Ion', 'IonChannel',

  # ions
  'Calcium',

  # ion channels
  'IhChannel', 'CalciumChannel', 'SodiumChannel', 'PotassiumChannel', 'LeakyChannel',
]


class Ion(Channel):
  """Base class for ions."""

  '''The type of the master object.'''
  master_type = CondNeuGroup

  def update(self, t, dt, V):
    raise NotImplementedError('Must be implemented by the subclass.')

  def reset(self, V):
    raise NotImplementedError('Must be implemented by the subclass.')

  def current(self, V):
    raise NotImplementedError('Must be implemented by the subclass.')

  def __repr__(self):
    return f'{self.__class__.__name__}(size={self.size})'


class IonChannel(Channel):
  """Base class for ion channels."""

  '''The type of the master object.'''
  master_type = CondNeuGroup

  def update(self, t, dt, V):
    raise NotImplementedError('Must be implemented by the subclass.')

  def current(self, V):
    raise NotImplementedError('Must be implemented by the subclass.')

  def reset(self, V):
    raise NotImplementedError('Must be implemented by the subclass.')

  def __repr__(self):
    return f'{self.__class__.__name__}(size={self.size})'


class Calcium(Ion, Container):
  """The base calcium dynamics.

  Parameters
  ----------
  size: int, sequence of int
    The size of the simulation target.
  method: str
    The numerical integration method.
  name: str
    The name of the object.
  **channels
    The calcium dependent channels.
  """

  '''The type of the master object.'''
  master_type = CondNeuGroup

  """Reversal potential."""
  E: Union[float, bm.Variable, bm.JaxArray]

  """Calcium concentration."""
  C: Union[float, bm.Variable, bm.JaxArray]

  def __init__(
      self,
      size: Shape,
      keep_size: bool = False,
      method: str = 'exp_auto',
      name: str = None,
      **channels
  ):
    Ion.__init__(self, size, keep_size=keep_size)
    Container.__init__(self, name=name, **channels)
    self.method = method

  def current(self, V, C_Ca=None, E_Ca=None):
    C_Ca = self.C if (C_Ca is None) else C_Ca
    E_Ca = self.E if (E_Ca is None) else E_Ca
    nodes = list(self.nodes(level=1, include_self=False).unique().subset(Channel).values())
    current = nodes[0].current(V, C_Ca, E_Ca)
    for node in nodes[1:]:
      current += node.current(V, C_Ca, E_Ca)
    return current

  def register_implicit_nodes(self, *channels, **named_channels):
    check_master(type(self), *channels, **named_channels)
    super(Calcium, self).register_implicit_nodes(*channels, **named_channels)


class CalciumChannel(IonChannel):
  """Base class for Calcium ion channels."""

  '''The type of the master object.'''
  master_type = Calcium

  def update(self, t, dt, V, C_Ca, E_Ca):
    raise NotImplementedError

  def current(self, V, C_Ca, E_Ca):
    raise NotImplementedError

  def reset(self, V, C_Ca, E_Ca):
    raise NotImplementedError


class IhChannel(IonChannel):
  """Base class for Ih channel models."""
  master_type = CondNeuGroup


class PotassiumChannel(IonChannel):
  """Base class for potassium channel."""

  '''The type of the master object.'''
  master_type = CondNeuGroup


class LeakyChannel(IonChannel):
  """Base class for leaky channel."""
  master_type = CondNeuGroup


class SodiumChannel(IonChannel):
  """Base class for sodium channel."""
  master_type = CondNeuGroup
