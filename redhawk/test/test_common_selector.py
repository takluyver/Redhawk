#!/usr/bin/env python

""" Test the selector module in redhawk/common."""

import redhawk.common.selector as S
import redhawk.common.node as N
from .sample_last import tree

import nose

""" The sample tree that we will test the selectors on:
(define-function Factorial 
  ((define-variable n))
  ((if 
    (eq n 
      (constant 0))
    ((return 
      (constant 1)))
    ((return 
      (* n 
        (apply Factorial 
          ((- n 
            (constant 1))))))))))
"""

def TestEmptySelector():
  """ Test the Empty Selector (Should return all nodes)."""
  l = list(S.S()(tree))
  #print l, len(l)
  assert(len(l) == 18) # Number of nodes in the tree.
  return


def TestSelector():
  """ Test Basic Selectors - function, attributes, node_type"""
  s1 = S.S(node_type = 'DefineFunction')
  s2 = S.S(value = '0')
  s3 = S.S(function = lambda x: hasattr(x, 'value') and x.value == '1')

  l1 = list(s1(tree))
  l2 = list(s2(tree))
  l3 = list(s3(tree))

  assert(len(l1) == 1 and len(l2) == 1 and len(l3) == 2)

  r1, r2, r3, r4 = l1[0], l2[0], l3[0], l3[1]

  assert(r1.name == 'Factorial')
  assert(r2.GetName() == 'Constant')
  assert(r3.GetName() == 'Constant')
  assert(r4.GetName() == 'Constant')
  return

def TestSelectorNodeType():
  """ Test a Basic Selector that takes a node type as a class."""
  s1 = S.S(node_type = N.Constant)
  l1 = list(s1(tree))
  assert(len(l1) == 3)
  assert(l1[0].GetName() == 'Constant')
  assert(l1[1].GetName() == 'Constant')
  assert(l1[2].GetName() == 'Constant')
  return


def TestMatchOnlyCommonAttributes():
  """ Test Matching only common attributes."""
  s1 = S.S(value = '0', asdf = 'Haha',
      match_only_common_attributes=False)

  s2 = S.S(value = '0', asdf = 'Haha',
      match_only_common_attributes=True)

  l1 = list(s1(tree))
  l2 = list(s2(tree))
  assert(len(l1) == 0)
  assert(len(l2) == 1)
  assert(l2[0].GetName() == 'Constant')
  return

def TestCommonAttributesFunction1():
  """ Test match common attributes for lambda function - success."""
  s1 = S.S(function = lambda x:x.value == '0',
      match_only_common_attributes=True)

  l1 = list(s1(tree))
  assert(len(l1) == 1)
  assert(l1[0].GetName() == 'Constant')
  return


@nose.tools.raises(AttributeError)
def TestCommonAttributesFunction2():
  """ Test match common attributes for lambda function - failure."""
  s1 = S.S(function = lambda x:x.value == '0' and x.asdf == 'Haha',
      match_only_common_attributes=False)
  l1 = list(s1(tree))
  return


def TestAttributeMatcherFunction():
  """ Test Attribute Matcher Function."""
  s = S.S(attr_matcher = lambda x, y: x.lower() == y.lower(),
                 name = 'fAcToRiaL')
  l = list(s(tree))
  assert(len(l) == 2)
  # Depends on order of traversal
  assert(l[0].GetName() == 'DefineFunction')
  assert(l[1].GetName() == 'ReferVariable')
  return


def TestAnd():
  """ Test And selector combinator."""
  s1 = S.S(node_type = 'Constant')
  s2 = S.S(value = '1')

  l1 = list(s1.And(s2)(tree))
  assert(len(l1) == 2)
  return

def TestOr():
  """ Test Or selector combinator."""
  s1 = S.S(node_type = N.CallFunction)
  s2 = S.S(node_type = N.DefineFunction)

  l1 = list(s1.Or(s2)(tree))
  assert(len(l1) == 2)
  return


def TestHasParent():
  """ Test HasParent selector combinator."""
  s1 = S.S(node_type = N.ReferVariable)
  s2 = S.S(node_type = N.CallFunction)

  l1 = list(s1.HasParent(s2)(tree))
  assert(len(l1) == 1)
  assert(l1[0].GetName() == 'ReferVariable')
  return


def TestHasAncestor():
  """ Test HasAncestor selector combinator."""
  s1 = S.S(node_type = N.CallFunction)
  s2 = S.S(node_type = N.Return)

  l1 = list(s1.HasAncestor(s2)(tree))
  assert(len(l1) == 1)
  assert(l1[0].GetName() == 'CallFunction')
  return


def TestHasChild():
  """ Test HasChild selector combinator."""
  s1 = S.S(node_type = N.CallFunction)
  s2 = S.S(node_type = N.ReferVariable)

  l1 = list(s1.HasChild(s2)(tree))
  assert(len(l1) == 1)
  assert(l1[0].GetName() == 'CallFunction')
  return


def TestHasDescendant():
  """ Test HasDescendant selector combinator."""
  s1 = S.S(node_type = N.Return)
  s2 = S.S(node_type = N.CallFunction)

  l1 = list(s1.HasDescendant(s2)(tree))
  assert(len(l1) == 1)
  assert(l1[0].GetName() == 'Return')
  return

def TestApply():
  return_node = S.S(node_type = N.Return)
  # Test on a single module node
  result = list(return_node.Apply([tree]))
  assert(len(result) == 2) # 2 return statements
  (r1, t1), (r2, t2) = result
  assert(t1 == tree and t2 == tree)
  assert(isinstance(r1, N.Return))
  assert(isinstance(r2, N.Return))

  constant_node = S.S(node_type = N.Constant)
  d = list(constant_node.Apply([r1, r2]))

  assert(len(d) == 2) # 2 constant nodes should have been found.
  (c1, p1), (c2, p2) = d
  assert(p1 != p2)
  assert(p1 == r1 or p2 == r1)
  assert(p1 == r2 or p2 == r2)

  assert(c1 != c2)
  assert(c1.value == c2.value == "1")
  return
